import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from playwright.async_api import async_playwright
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.database import AsyncSessionLocal
from app.models import Car
from app.scraper.parser import scrape_brand
from app.scraper.translations import BRAND_CODES

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def scrape_job() -> None:
    """Основная задача: парсит все марки и сохраняет в БД."""
    logger.info("Запуск парсера...")
    total_saved = 0

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        try:
            for brand_code in BRAND_CODES:
                cars = await scrape_brand(browser, brand_code)
                saved = await save_cars(cars)
                total_saved += saved
                logger.info("Сохранено %d авто для %s", saved, brand_code)
        finally:
            await browser.close()

    logger.info("Парсер завершён. Всего сохранено: %d", total_saved)


async def save_cars(cars) -> int:
    """Upsert: вставляет новые авто или обновляет существующие по url."""
    if not cars:
        return 0

    saved = 0
    async with AsyncSessionLocal() as session:
        for car in cars:
            if not car.url:
                continue

            stmt = (
                insert(Car)
                .values(
                    brand=car.brand,
                    model=car.model,
                    year=car.year,
                    mileage=car.mileage,
                    price=car.price,
                    transmission=car.transmission,
                    body_type=car.body_type,
                    engine_volume=car.engine_volume,
                    fuel_type=car.fuel_type,
                    drive_type=car.drive_type,
                    color=car.color,
                    has_accidents=car.has_accidents,
                    photos=car.photos,
                    url=car.url,
                )
                .on_conflict_do_update(
                    index_elements=["url"],
                    set_={
                        "brand": car.brand,
                        "model": car.model,
                        "price": car.price,
                        "mileage": car.mileage,
                        "transmission": car.transmission,
                        "body_type": car.body_type,
                        "engine_volume": car.engine_volume,
                        "fuel_type": car.fuel_type,
                        "drive_type": car.drive_type,
                        "color": car.color,
                        "has_accidents": car.has_accidents,
                        "photos": car.photos,
                        "updated_at": Car.updated_at,
                    },
                )
            )
            await session.execute(stmt)
            saved += 1

        await session.commit()

    return saved


def start_scheduler() -> None:
    scheduler.add_job(scrape_job, "interval", hours=1, id="scrape_job", replace_existing=True)
    scheduler.start()
    logger.info("Планировщик запущен (каждый час)")
