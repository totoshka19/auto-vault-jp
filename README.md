# AutoVault JP

Каталог японских автомобилей с CarSensor.net — тестовое задание.

## Ссылки

- **Приложение**: https://frontend-gold-five-63.vercel.app
- **GitHub**: https://github.com/totoshka19/auto-vault-jp
- **Backend API**: https://auto-vault-jp.onrender.com

## Вход

| Логин | Пароль   |
|-------|----------|
| admin | admin123 |

## Стек

**Frontend**
- Next.js 15 (App Router, TypeScript)
- Mantine UI v7 (компоненты, карусель)
- TanStack Query v5 (кеш запросов)
- Zustand (хранение JWT-токена)
- Axios (HTTP-клиент)

**Backend**
- FastAPI + Python 3.11
- SQLAlchemy (async) + PostgreSQL (Neon)
- Alembic (миграции)
- Playwright (парсер CarSensor.net)
- APScheduler (запуск парсера каждый час)
- JWT-авторизация (passlib + python-jose)

**Деплой**
- Frontend — Vercel
- Backend — Render
- БД — Neon (PostgreSQL)

## Локальный запуск

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Создать backend/.env:
# DATABASE_URL=...
# SECRET_KEY=...
# ALLOWED_ORIGINS=http://localhost:3000

alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install

# Создать frontend/.env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev
```

Открыть http://localhost:3000

## Парсер

- Запускается автоматически при старте бэкенда и далее каждый час
- Парсит 10 брендов с CarSensor.net (Toyota, Nissan, Honda и др.)
- Сохраняет/обновляет авто в БД по `url` (upsert)
- Один полный прогон — около 20 минут
