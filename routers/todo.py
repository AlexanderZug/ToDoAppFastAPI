from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
)
from starlette import status

from models import ToDo
from db import SessionLocal
from routers.auth import get_current_user


router = APIRouter(
    prefix='/todo',
    tags=['todo'],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class ToDoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=3, max_length=150)
    priority: int = Field(gt=0, lt=6)
    completed: bool


@router.get('/{todo_id}/', status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')

    todo_model = db.query(ToDo).filter(
        ToDo.id == todo_id
    ).filter(
        ToDo.owner_id == user.get('id')
    ).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='ToDo not found')


@router.get('/me', status_code=status.HTTP_200_OK)
async def read_user_todos(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    return db.query(ToDo).filter(ToDo.owner_id == user.get('id')).all()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_todo(
        user: user_dependency,
        db: db_dependency,
        todo_request: ToDoRequest,
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    todo_model = ToDo(**todo_request.dict(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()
    return todo_model


@router.put('/{todo_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
        user: user_dependency,
        db: db_dependency,
        todo_request: ToDoRequest,
        todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')

    todo_model = db.query(ToDo).filter(
        ToDo.id == todo_id
    ).filter(ToDo.owner_id == user.get('id')
             ).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ToDo not found')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.completed = todo_request.completed

    db.add(todo_model)
    db.commit()


@router.delete('/{todo_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
        user: user_dependency,
        db: db_dependency,
        todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')

    todo_model = db.query(ToDo).filter(
        ToDo.id == todo_id
    ).filter(
        ToDo.owner_id == user.get('id')
    ).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ToDo not found')

    db.delete(todo_model)
    db.commit()
