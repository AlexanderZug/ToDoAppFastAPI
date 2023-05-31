from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from models import ToDo
from fastapi import FastAPI, Depends, HTTPException, Path
from starlette import status
from db import engine, SessionLocal


app = FastAPI()

models.Base.metadata.create_all(bind=engine)


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


@app.get('/', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(ToDo).all()


@app.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='ToDo not found')


@app.post('/todo', status_code=status.HTTP_201_CREATED)
async def create_todo(
        db: db_dependency,
        todo_request: ToDoRequest,
):
    todo_model = ToDo(**todo_request.dict())
    db.add(todo_model)
    db.commit()
    return todo_model


@app.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
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
