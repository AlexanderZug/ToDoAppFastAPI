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


class ToDoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=3, max_length=150)
    priority: int = Field(gt=0, lt=6)
    completed: bool


@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(ToDo).all()


@router.get('/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='ToDo not found')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_todo(
        db: db_dependency,
        todo_request: ToDoRequest,
):
    todo_model = ToDo(**todo_request.dict())
    db.add(todo_model)
    db.commit()
    return todo_model


@router.put('/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
        db: db_dependency,
        todo_request: ToDoRequest,
        todo_id: int = Path(gt=0),
):
    todo_model = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ToDo not found')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.completed = todo_request.completed

    db.add(todo_model)
    db.commit()


@router.delete('/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
        db: db_dependency,
        todo_id: int = Path(gt=0),
):
    todo_model = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='ToDo not found')

    db.delete(todo_model)
    db.commit()
