# 🚀 REST API на FastAPI с Celery, Redis и PostgreSQL

## Описание проекта

   Этот проект реализует полноценный REST API на FastAPI с поддержкой:

   - Асинхронного API (FastAPI + async SQLAlchemy)
   - Отправки email и webhook задач через Celery
   - Redis как брокера и backend для Celery
   - PostgreSQL как основную базу данных
   - Alembic для миграций
   - Poetry как менеджера зависимостей
   - Полноценной Docker-инфраструктуры


## Установка
   Склонируйте репозиторий:
   ```bash
   git clone git@github.com:JacobKleim/FastAPI_Tasks.git
   ```

## Poetry + Зависимости
   Обновите pip:
   ```bash
   pip install --upgrade pip
   ```
   Установите Poetry (если не установлен):
   ```bash
   pip install poetry
   ```
   Установите зависимости проекта:
   ```bash
   poetry install
   ```
   Добавить новые зависимости(если необходимо):
   ```bash
   poetry add some_library
   ```


## Переменные окружения:
   В корневом каталоге создайте файл .env и добавьте в него ваши данные для БД и секретный ключ.
   Пример:
   ```bash
   DATABASE_URL=postgresql+asyncpg://fastapi_user:fastapi_password@localhost:5432/fastapi_db
   SYNC_DATABASE_URL=postgresql+psycopg2://fastapi_user:fastapi_password@localhost:5432/fastapi_db

   SECRET_KEY=mysecretkey
   DEBUG=True
   ACCESS_TOKEN_EXPIRE_SECONDS=3600

   POSTGRES_USER=fastapi_user
   POSTGRES_PASSWORD=fastapi_password
   POSTGRES_DB=fastapi_db

   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND_URL=redis://localhost:6379/0

   EMAIL=your_mail@google.com
   EMAIL_PASSWORD=your_password
   ```

## База данных
   База данных на PostgreSQL и Redis работает в docker контейнере. Установите [Docker](https://www.docker.com/), соберите и запустите контейнеры:
   ```bash
   docker-compose up --build -d
   ```

## Миграции
   Примените существующие миграции Alembic:
   ```bash
   docker compose exec app poetry run alembic upgrade head
   ```
   Если необходимо создать новые миграции, то используйте команду:
   ```bash
   docker compose exec app poetry run alembic revision --autogenerate -m "Information about migration"
   ```
   После создания новой миграции снова используйте команду для применения миграций.

## Запуск
   Запуск сервера разработки:
   ```bash
   docker compose exec app poetry run uvicorn app.main:app --reload
   ```

## Тестирование
   Для запуска тестов выполните:
   ```bash
   docker compose exec app poetry run pytest
   ```

## Celery: асинхронные задачи
   Проект использует Celery для асинхронной обработки задач.

   Запуск воркера:
   ```bash
   poetry run celery -A app.celery_tasks.notifications worker --loglevel=info --pool=solo
   ```
   - --pool=solo подходит для Windows или разработки.
   - В Linux используйте --pool=prefork или --pool=threads
   ### *Изменения необходимо вносить в docker-compose файл*
   
   Celery worker logs:
   ```bash
   docker compose logs -f worker
   ```



## Разделение задач по воркерам (опционально)
   Если ты хочешь разделить задачи (например, email и webhook) на разные очереди:
   ```bash
   poetry run celery -A app.celery_tasks.notifications worker --loglevel=info --queues=email_queue
   poetry run celery -A app.celery_tasks.notifications worker --loglevel=info --queues=webhook_queue
   ```
   ### *Изменения необходимо вносить в docker-compose файл*
