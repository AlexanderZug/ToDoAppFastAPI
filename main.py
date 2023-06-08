import models
from fastapi import FastAPI

from db import engine
from routers import auth, todo, admin, user, address


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(address.router)
