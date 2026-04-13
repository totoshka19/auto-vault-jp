import math
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Car
from app.schemas import CarRead, CarsListResponse

router = APIRouter(prefix="/cars", tags=["cars"])


@router.get("", response_model=CarsListResponse)
async def list_cars(
    brand: str | None = Query(None),
    model: str | None = Query(None),
    year_from: int | None = Query(None),
    year_to: int | None = Query(None),
    price_min: int | None = Query(None),
    price_max: int | None = Query(None),
    mileage_min: int | None = Query(None),
    mileage_max: int | None = Query(None),
    sort: Literal["price", "year", "mileage"] = Query("price"),
    order: Literal["asc", "desc"] = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    _: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if brand:
        filters.append(Car.brand.ilike(f"%{brand}%"))
    if model:
        filters.append(Car.model.ilike(f"%{model}%"))
    if year_from:
        filters.append(Car.year >= year_from)
    if year_to:
        filters.append(Car.year <= year_to)
    if price_min:
        filters.append(Car.price >= price_min)
    if price_max:
        filters.append(Car.price <= price_max)
    if mileage_min:
        filters.append(Car.mileage >= mileage_min)
    if mileage_max:
        filters.append(Car.mileage <= mileage_max)

    sort_column = getattr(Car, sort)
    order_expr = sort_column.asc() if order == "asc" else sort_column.desc()

    count_result = await db.execute(select(func.count()).select_from(Car).where(*filters))
    total = count_result.scalar_one()

    offset = (page - 1) * limit
    result = await db.execute(
        select(Car).where(*filters).order_by(order_expr).offset(offset).limit(limit)
    )
    cars = result.scalars().all()

    return CarsListResponse(
        items=cars,
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit) if total else 0,
    )


@router.get("/{car_id}", response_model=CarRead)
async def get_car(
    car_id: int,
    _: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    if car is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    return car
