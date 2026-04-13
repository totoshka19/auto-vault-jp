from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, cars
from app.scraper.worker import scrape_job, start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    await scrape_job()  # первый запуск при старте
    yield


app = FastAPI(title="AutoVault JP API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cars.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
