import os
from datetime import timedelta, datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic.fields import Field
from pydantic.main import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from jose import jwt, JWTError
from dotenv import load_dotenv

from db import SessionLocal
from models import User


load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.environ.get('ALGORITHM')

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class UserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=150)
    phone_number: Optional[str]
    email: str = Field(min_length=4, max_length=50)
    role: str = Field(min_length=3, max_length=50)


class TokenRequest(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    to_encode = {
        'sub': username,
        'id': user_id,
        'role': role,
    }
    expires = datetime.utcnow() + expires_delta
    to_encode.update({'exp': expires})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise credentials_exception
        token_data = TokenRequest(access_token=token, token_type='bearer')
    except JWTError:
        raise credentials_exception
    return {'username': username, 'id': user_id, 'user_role': user_role, 'token': token_data}


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(
        db: db_dependency,
        user_request: UserRequest,
):
    create_user_model = User(
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=bcrypt_context.hash(user_request.password),
        phone_number=user_request.phone_number,
        email=user_request.email,
        role=user_request.role,
    )

    db.add(create_user_model)
    db.commit()
    return create_user_model.username


@router.post('/token', response_model=TokenRequest, status_code=status.HTTP_200_OK)
async def login_for_access_token(
        db: db_dependency,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
        )
    token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=15),
    )
    return {'access_token': token, 'token_type': 'bearer'}
