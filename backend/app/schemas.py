from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CarBase(BaseModel):
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    mileage: int | None = None
    price: int | None = None
    transmission: str | None = None
    body_type: str | None = None
    engine_volume: str | None = None
    fuel_type: str | None = None
    drive_type: str | None = None
    color: str | None = None
    has_accidents: bool | None = None
    photos: list[str] | None = None
    url: str | None = None


class CarRead(CarBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class CarsListResponse(BaseModel):
    items: list[CarRead]
    total: int
    page: int
    limit: int
    pages: int


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
