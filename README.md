# Tasks

## Описание проекта
   Асинхронный REST API на FastAPI с использованием PostgreSQL, асинхронным SQLAlchemy, Alembic, Docker и поддержкой поддержкой автотестов.


## Установка
   Склонируйте репозиторий:
   ```
   git@github.com:JacobKleim/FastAPI_Tasks.git
   ```

## Виртуальное окружение      
  Создайте и активируйте виртуальное окружение:
   ```
   python -m venv venv
   ```
   For Windows:
   ```bash
   source venv/Scripts/activate
   ```
   For Linux:
   ```bash
   source venv/bin/activate
   ```


## Зависимости
  Обновите pip и установите зависимости:
   ```
   python -m pip install --upgrade pip
   ```
   ```
   pip install -r requirements.txt
   ```

## Переменные окружения:
   В корневом каталоге создайте файл .env и добавьте в него ваши данные для БД и секретный ключ:
   ```
   DATABASE_URL=postgresql+asyncpg://fastapi_user:fastapi_password@localhost:5432/fastapi_db
   SYNC_DATABASE_URL=postgresql+psycopg2://fastapi_user:fastapi_password@localhost:5432/fastapi_db
   SECRET_KEY=mysecretkey
   DEBUG=True
   ACCESS_TOKEN_EXPIRE_SECONDS=3600
   POSTGRES_USER=fastapi_user
   POSTGRES_PASSWORD=fastapi_password
   POSTGRES_DB=fastapi_db
   ```

## База данных
   База данных на PostgreSQL работает в docker контейнере. Установите Docker и запустите контейнер:
   ```
   docker compose up -d
   ```

## Миграции
   Примените существующие миграции Alembic:
   ```
   alembic upgrade head
   ```
   Если необходимо создать новые миграции, то используйте команду:
   ```
   alembic revision --autogenerate -m "Information about migration"
   ```
   После создания новой миграции снова используйте команду для применения миграций.

## Запуск
   Запуск сервера разработки:
   ```
   uvicorn app.main:app --reload
   ```

## Тестирование
   Для запуска тестов выполните:
   ```
   pytest
   ```
