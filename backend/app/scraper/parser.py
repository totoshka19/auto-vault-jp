import asyncio
import logging
import re
from dataclasses import dataclass, field

from bs4 import BeautifulSoup
from playwright.async_api import Browser, Page

from app.scraper.translations import (
    ACCIDENT_HISTORY,
    BODY_TYPE,
    BRAND_CODES,
    DRIVE_TYPE,
    FIELD_MAP,
    FUEL_TYPE,
    translate_color,
    translate_transmission,
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
    """'660cc' → '0.66 л', '2000cc' → '2.0 л', '2.8L' → '2.8 л'"""
    value = value.strip()
    if not value or value == "－":
        return None
    # Уже в литрах: '2.8L'
    m = re.match(r'^(\d+\.?\d*)[Ll]$', value)
    if m:
        liters = float(m.group(1))
        s = f"{liters:.2f}".rstrip('0')
        if s.endswith('.'): s += '0'
        return f"{s} л"
    # В кубиках: '660cc', '2000cc'
    m = re.match(r'^(\d+)[Cc]{2}$', value)
    if m:
        liters = int(m.group(1)) / 1000
        if liters == int(liters):
            return f"{int(liters)}.0 л"
        s = f"{liters:.2f}".rstrip('0')
        if s.endswith('.'): s += '0'
        return f"{s} л"
    return value


def strip_japanese(text: str) -> str:
    """Удаляет японские/CJK символы, оставляет ASCII и цифры."""
    cleaned = re.sub(r'[\u3000-\u9FFF\uFF00-\uFFEF（）「」【】・]+', ' ', text)
    return ' '.join(cleaned.split()).strip()


_JP_PAT = re.compile(r'[\u3000-\u9FFF\uFF00-\uFFEF（）「」【】・]+')


def translate_dict(d: dict, value: str) -> str | None:
    """Переводит по словарю; если не найдено — убирает японские символы."""
    if value in d:
        return d[value]
    cleaned = _JP_PAT.sub(' ', value).strip()
    cleaned = ' '.join(cleaned.split())
    return cleaned if cleaned else None


def clean_model(text: str) -> str:
    """Убирает японские символы и мусорные слеши из названия модели."""
    stripped = strip_japanese(text)
    # Разбиваем по слешам, оставляем только содержательные части
    # (не пустые, не одиночные числа вроде '19' или '2019')
    parts = re.split(r'\s*/\s*', stripped)
    meaningful = [p.strip() for p in parts if p.strip() and not re.match(r"^'?\d{2,4}$", p.strip())]
    return ' '.join(meaningful).strip()


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
            car.transmission = translate_transmission(value)
        elif field_name == "body_type":
            car.body_type = translate_dict(BODY_TYPE, value)
        elif field_name == "engine_volume":
            car.engine_volume = parse_engine_volume(value)
        elif field_name == "fuel_type":
            car.fuel_type = translate_dict(FUEL_TYPE, value)
        elif field_name == "drive_type":
            car.drive_type = translate_dict(DRIVE_TYPE, value)
        elif field_name == "color":
            car.color = translate_color(value)
        elif field_name == "has_accidents":
            car.has_accidents = ACCIDENT_HISTORY.get(value)

    # Главное фото: img[data-photo] на ccsrpcma CDN (превью в каталоге)
    ma_cdn = re.compile(r"ccsrpcma\.carsensor\.net/CSphoto")
    for img in soup.find_all("img", attrs={"data-photo": True}):
        src = img.get("data-photo", "")
        if ma_cdn.search(src) and src not in car.photos:
            car.photos.append(src)
            break  # Только одно главное фото

    # Все фото галереи: a[data-photo] на ccsrpcml CDN
    ml_cdn = re.compile(r"ccsrpcml\.carsensor\.net/CSphoto")
    for a in soup.find_all("a", attrs={"data-photo": True}):
        src = a.get("data-photo", "")
        if ml_cdn.search(src) and src not in car.photos:
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
                car.brand = BRAND_CODES.get(brand_code, car.brand)
                if car.model:
                    car.model = clean_model(car.model)[:100] or car.model[:100]
                results.append(car)
            await asyncio.sleep(1.5)
    finally:
        await context.close()

    return results
