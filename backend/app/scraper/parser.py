import asyncio
import logging
import re
from dataclasses import dataclass, field

from bs4 import BeautifulSoup
from playwright.async_api import Browser, Page

from app.scraper.translations import (
    ACCIDENT_HISTORY,
    BODY_TYPE,
    DRIVE_TYPE,
    FIELD_MAP,
    FUEL_TYPE,
    TRANSMISSION,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://www.carsensor.net"


@dataclass
class CarData:
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
    photos: list[str] = field(default_factory=list)
    url: str | None = None


# --- Конвертеры ---

def parse_man_km(value: str) -> int | None:
    """'3.4万km' → 34000"""
    try:
        cleaned = value.replace("万km", "").replace(",", "").strip()
        return int(float(cleaned) * 10000)
    except (ValueError, AttributeError):
        return None


def parse_man_yen(value: str) -> int | None:
    """'460.9万円' → 4609000"""
    try:
        cleaned = value.replace("万円", "").replace(",", "").strip()
        return int(float(cleaned) * 10000)
    except (ValueError, AttributeError):
        return None


def parse_year(value: str) -> int | None:
    """'2024(R06)' → 2024"""
    try:
        return int(value[:4])
    except (ValueError, TypeError):
        return None


def parse_engine_volume(value: str) -> str | None:
    """'2800cc' → '2800cc', '2.8L' → '2.8L'"""
    value = value.strip()
    return value if value and value != "－" else None


# --- Сбор ссылок на детальные страницы ---

async def collect_detail_urls(page: Page, brand_code: str) -> list[str]:
    """Собирает все ссылки на детальные страницы для марки."""
    urls: list[str] = []
    list_url = f"{BASE_URL}/usedcar/{brand_code}/index.html"
    page_num = 1

    while True:
        url = f"{BASE_URL}/usedcar/{brand_code}/index.html?page={page_num}" if page_num > 1 else list_url
        logger.info("Собираю ссылки: %s", url)

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            logger.warning("Не удалось загрузить страницу %s: %s", url, e)
            break

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        detail_links = soup.select("a[href*='/usedcar/detail/']")
        if not detail_links:
            break

        for link in detail_links:
            href = link.get("href", "")
            full_url = BASE_URL + href if href.startswith("/") else href
            # Берём только /usedcar/detail/.../index.html
            if re.search(r"/usedcar/detail/[A-Z0-9]+/index\.html", full_url):
                if full_url not in urls:
                    urls.append(full_url)

        # Проверяем наличие следующей страницы
        next_btn = soup.select_one("a.nextPage, a[rel='next']")
        if not next_btn:
            break

        page_num += 1
        await asyncio.sleep(1.5)

    return urls


# --- Парсинг детальной страницы ---

async def parse_detail_page(page: Page, url: str) -> CarData | None:
    """Парсит детальную страницу автомобиля."""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        logger.warning("Не удалось загрузить %s: %s", url, e)
        return None

    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    car = CarData(url=url)

    # Марка и модель из <h1>
    h1 = soup.find("h1")
    if h1:
        text = h1.get_text(separator=" ", strip=True)
        parts = text.split()
        if len(parts) >= 2:
            car.brand = parts[0][:100]
            car.model = " ".join(parts[1:])[:100]
        else:
            car.model = text[:100]

    # Характеристики из таблиц th/td
    for th in soup.find_all("th"):
        key = th.get_text(strip=True)
        td = th.find_next_sibling("td")
        if not td:
            continue
        value = td.get_text(strip=True)
        field_name = FIELD_MAP.get(key)

        if field_name == "year":
            car.year = parse_year(value)
        elif field_name == "mileage":
            car.mileage = parse_man_km(value)
        elif field_name == "price":
            car.price = parse_man_yen(value)
        elif field_name == "transmission":
            car.transmission = TRANSMISSION.get(value, value)
        elif field_name == "body_type":
            car.body_type = BODY_TYPE.get(value, value)
        elif field_name == "engine_volume":
            car.engine_volume = parse_engine_volume(value)
        elif field_name == "fuel_type":
            car.fuel_type = FUEL_TYPE.get(value, value)
        elif field_name == "drive_type":
            car.drive_type = DRIVE_TYPE.get(value, value)
        elif field_name == "color":
            car.color = value if value != "－" else None
        elif field_name == "has_accidents":
            car.has_accidents = ACCIDENT_HISTORY.get(value)

    # Фотографии с CDN
    for img in soup.find_all("img", src=re.compile(r"ccsrpcma\.carsensor\.net/CSphoto")):
        src = img.get("src", "")
        if src and src not in car.photos:
            car.photos.append(src)

    return car


# --- Основная функция парсинга одной марки ---

async def scrape_brand(browser: Browser, brand_code: str) -> list[CarData]:
    """Парсит все автомобили одной марки."""
    context = await browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        locale="ja-JP",
        extra_http_headers={
            "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
        },
    )
    page = await context.new_page()
    results: list[CarData] = []

    try:
        detail_urls = await collect_detail_urls(page, brand_code)
        logger.info("Найдено %d авто для %s", len(detail_urls), brand_code)

        for url in detail_urls:
            car = await parse_detail_page(page, url)
            if car and car.price:
                results.append(car)
            await asyncio.sleep(1.5)
    finally:
        await context.close()

    return results
