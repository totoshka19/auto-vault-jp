"""
Одноразовый скрипт: чистит старые записи в БД.
- Убирает японские символы из model
- Переводит transmission/body_type/fuel_type/drive_type/brand
- Исправляет brand по BRAND_CODES (для старых записей с японским брендом)

Запуск: python -m scripts.cleanup_db
(из папки backend/, с активным .venv)
"""

import asyncio
import re

from sqlalchemy import select, update

from app.database import AsyncSessionLocal
from app.models import Car
from app.scraper.translations import (
    BODY_TYPE,
    BRAND_CODES,
    DRIVE_TYPE,
    FUEL_TYPE,
    TRANSMISSION,
)

# Словарь для исправления японских названий брендов
JAPANESE_BRANDS: dict[str, str] = {
    "トヨタ": "Toyota",
    "日産": "Nissan",
    "ホンダ": "Honda",
    "三菱": "Mitsubishi",
    "スバル": "Subaru",
    "マツダ": "Mazda",
    "ダイハツ": "Daihatsu",
    "スズキ": "Suzuki",
    "レクサス": "Lexus",
    "フォルクスワーゲン": "Volkswagen",
}

JAPANESE_PATTERN = re.compile(r'[\u3000-\u9FFF\uFF00-\uFFEF（）「」【】・]+')


def strip_japanese(text: str) -> str:
    cleaned = JAPANESE_PATTERN.sub(' ', text)
    return ' '.join(cleaned.split()).strip()


async def main() -> None:
    updated = 0
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Car))
        cars = result.scalars().all()

        for car in cars:
            changed = False

            # Бренд: исправить японские названия
            if car.brand and JAPANESE_PATTERN.search(car.brand):
                new_brand = JAPANESE_BRANDS.get(car.brand, car.brand)
                if new_brand != car.brand:
                    car.brand = new_brand
                    changed = True

            # Модель: убрать японские символы
            if car.model and JAPANESE_PATTERN.search(car.model):
                cleaned = strip_japanese(car.model)
                if cleaned:
                    car.model = cleaned[:100]
                    changed = True

            # Трансмиссия
            if car.transmission and car.transmission in TRANSMISSION:
                new_val = TRANSMISSION[car.transmission]
                if new_val != car.transmission:
                    car.transmission = new_val
                    changed = True

            # Тип кузова
            if car.body_type and car.body_type in BODY_TYPE:
                new_val = BODY_TYPE[car.body_type]
                if new_val != car.body_type:
                    car.body_type = new_val
                    changed = True

            # Тип топлива
            if car.fuel_type and car.fuel_type in FUEL_TYPE:
                new_val = FUEL_TYPE[car.fuel_type]
                if new_val != car.fuel_type:
                    car.fuel_type = new_val
                    changed = True

            # Привод
            if car.drive_type and car.drive_type in DRIVE_TYPE:
                new_val = DRIVE_TYPE[car.drive_type]
                if new_val != car.drive_type:
                    car.drive_type = new_val
                    changed = True

            if changed:
                updated += 1

        await session.commit()

    print(f"Обновлено записей: {updated}")


if __name__ == "__main__":
    asyncio.run(main())
