import sys
from typing import Optional

sys.path.append("..")

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

import models
from db import SessionLocal, engine
from routers.auth import get_current_user


router = APIRouter(
    prefix='/address',
    tags=['address'],
    responses={404: {'description': 'Not found'}},
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Depends(get_db)


class AddressRequest(BaseModel):
    street: str = Field(min_length=3, max_length=50)
    city: str = Field(min_length=3, max_length=50)
    state: str = Field(min_length=3, max_length=50)
    country: str = Field(min_length=3, max_length=50)
    postal_code: str = Field(min_length=3, max_length=50)
    apartment_number: Optional[int]


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_address(
        address_request: AddressRequest,
        user: dict = Depends(get_current_user),
        db: Session = db_dependency,
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')

    address = models.Address(
        street=address_request.street,
        city=address_request.city,
        state=address_request.state,
        country=address_request.country,
        postal_code=address_request.postal_code,
        apartment_number=address_request.apartment_number,
    )
    db.add(address)
    db.flush()

    user_model = db.query(models.User).filter(models.User.id == user.get('id')).first()
    user_model.address_id = address.id
    db.add(user_model)
    db.commit()
