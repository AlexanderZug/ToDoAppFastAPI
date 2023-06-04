from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from passlib.context import CryptContext
from starlette import status

from models import User
from db import SessionLocal
from routers.auth import get_current_user


router = APIRouter(
    prefix='/user',
    tags=['user'],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class PasswordRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=5, max_length=50)


@router.get('/me', status_code=status.HTTP_200_OK)
async def read_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    return db.query(User).filter(User.id == user.get('id')).first()


@router.put('/change_password', status_code=status.HTTP_204_NO_CONTENT)
async def update_password(
        user: user_dependency,
        db: db_dependency,
        password_request: PasswordRequest,
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')

    user = db.query(User).filter(User.id == user.get('id')).first()
    if not bcrypt_context.verify(password_request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid password')

    user.hashed_password = bcrypt_context.hash(password_request.password)
    db.add(user)
    db.commit()

    return {'message': 'Password updated'}
