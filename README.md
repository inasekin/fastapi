# Task Manager — FastAPI + MySQL + Docker

[![Maintainability](https://qlty.sh/gh/inasekin/projects/fastapi/maintainability.svg)](https://qlty.sh/gh/inasekin/projects/fastapi)

REST API + SPA-фронтенд для управления задачами. FastAPI-бэкенд + MySQL в разных Docker-контейнерах, связанных через Docker-compose. Данные сохраняются в named volume при остановке/удалении контейнеров.

---

## Архитектура контейнеров

```
┌─────────────────────────────────────────┐
│            Docker network               │
│                                         │
│  ┌─────────────┐     ┌───────────────┐  │
│  │   frontend  │────▶│    backend    │  │
│  │  nginx:80   │     │  FastAPI:8000 │  │
│  └─────────────┘     └──────┬────────┘  │
│                              │           │
│                       ┌──────▼────────┐  │
│                       │      db       │  │
│                       │  MySQL:3306   │  │
│                       └──────┬────────┘  │
│                              │           │
│                       ┌──────▼────────┐  │
│                       │  mysql_data   │  │
│                       │   (volume)    │  │
│                       └───────────────┘  │
└─────────────────────────────────────────┘
```

| Контейнер | Образ                  | Порт (хост) | Назначение                        |
|-----------|------------------------|-------------|-----------------------------------|
| `db`      | `mysql:8.0`            | —           | СУБД, данные в named volume       |
| `backend` | сборка `backend/`      | `8000`      | FastAPI REST API                  |
| `frontend`| сборка `frontend/`     | `80`        | Nginx + SPA, проксирует `/api/`   |

---

## Быстрый старт через Docker Compose

### 1. Клонировать репозиторий

```bash
git clone <repo-url>
cd fastapi
```

### 2. Создать файл `.env`

```bash
cp .env.example .env
```

Отредактировать при необходимости — все переменные имеют безопасные значения по умолчанию.

Ключевые переменные:

| Переменная           | По умолчанию                              | Описание                              |
|----------------------|-------------------------------------------|---------------------------------------|
| `MYSQL_ROOT_PASSWORD`| `rootpassword`                            | Пароль root MySQL                     |
| `MYSQL_DATABASE`     | `taskdb`                                  | Имя базы данных                       |
| `MYSQL_USER`         | `taskuser`                                | Пользователь MySQL для приложения     |
| `MYSQL_PASSWORD`     | `taskpassword`                            | Пароль этого пользователя             |
| `SECRET_KEY`         | `change-me-in-production-...`             | JWT-ключ (сменить в проде!)           |
| `BACKEND_PORT`       | `8000`                                    | Порт FastAPI на хосте                 |
| `FRONTEND_PORT`      | `80`                                      | Порт nginx на хосте                   |

Сгенерировать секретный ключ:

```bash
openssl rand -hex 32
```

### 3. Собрать и запустить

```bash
docker compose up --build -d
```

Первый запуск занимает ~2–3 минуты (сборка frontend и скачивание образов).

Проверить статус:

```bash
docker compose ps
```

### 4. Открыть в браузере

| URL                          | Что это                         |
|------------------------------|---------------------------------|
| <http://localhost>           | Веб-интерфейс (SPA)             |
| <http://localhost:8000/docs> | Swagger UI (FastAPI)            |
| <http://localhost:8000/redoc>| ReDoc                           |

### 5. Остановить

```bash
docker compose down
```

Данные MySQL **сохранятся** в volume `mysql_data`. Чтобы удалить и данные:

```bash
docker compose down -v
```

---

## Демонстрация сохранения данных через volume

```bash
# 1. Запустить стек
docker compose up -d

# 2. Создать пользователя и задачу через API
curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}' | python3 -m json.tool

# Получить токен
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token \
  -d "username=demo&password=demo123" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Создать задачу
curl -s -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Тест volume","description":"Данные сохраняются","status":"pending","priority":1}' \
  | python3 -m json.tool

# 3. Удалить контейнер БД
docker compose stop db
docker compose rm -f db

# 4. Поднять снова
docker compose up -d db
sleep 20

# 5. Убедиться, что задача сохранилась
curl -s -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## CRUD API

| Метод    | URL                       | Описание                          |
|----------|---------------------------|-----------------------------------|
| `POST`   | `/api/auth/register`      | Регистрация пользователя          |
| `POST`   | `/api/auth/token`         | Получить JWT-токен                |
| `GET`    | `/api/tasks`              | Список задач (сортировка)         |
| `POST`   | `/api/tasks`              | Создать задачу (Create)           |
| `GET`    | `/api/tasks/{id}`         | Получить задачу (Read)            |
| `PATCH`  | `/api/tasks/{id}`         | Обновить задачу (Update)          |
| `DELETE` | `/api/tasks/{id}`         | Удалить задачу (Delete)           |
| `GET`    | `/api/tasks/search?q=`    | Поиск по тексту                   |
| `GET`    | `/api/tasks/top-priority` | Топ-N задач по приоритету         |

---

## Docker Swarm (режим кластера)

Предварительно инициализировать Swarm и собрать образы:

```bash
docker swarm init

docker build -t task-manager-backend:latest ./backend
docker build -t task-manager-frontend:latest ./frontend
```

Запустить стек:

```bash
docker stack deploy -c docker-compose.swarm.yml task-manager
```

Проверить сервисы:

```bash
docker stack services task-manager
docker service ls
```

При падении любого контейнера Swarm автоматически перезапустит его. Состояние MySQL сохраняется в named volume.

Удалить стек:

```bash
docker stack rm task-manager
```

---

## Структура проекта

```
.
├── backend/
│   ├── app/
│   │   ├── main.py          # точка входа FastAPI
│   │   ├── models.py        # SQLAlchemy модели (User, Task)
│   │   ├── database.py      # подключение к БД
│   │   ├── config.py        # настройки через pydantic-settings
│   │   ├── schemas.py       # Pydantic-схемы
│   │   ├── security.py      # JWT, хэширование паролей
│   │   ├── deps.py          # зависимости FastAPI
│   │   ├── task_cache.py    # in-memory кэш списка задач
│   │   └── routers/
│   │       ├── auth.py      # /api/auth/*
│   │       └── tasks.py     # /api/tasks/*
│   ├── tests/               # pytest + locust load tests
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/
│   ├── src/                 # Vanilla JS SPA
│   ├── public/              # index.html, CSS
│   ├── Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml       # основной оркестратор
├── docker-compose.swarm.yml # Docker Swarm стек
├── .env.example             # шаблон переменных окружения
└── README.md
```

---

## Локальная разработка (без Docker)

Требования: [uv](https://docs.astral.sh/uv/), Node.js 18+, GNU Make.

```bash
make install

# В двух терминалах:
make dev-backend    # API: http://127.0.0.1:8000
make dev-frontend   # UI:  http://127.0.0.1:8080
```

Запуск тестов:

```bash
make test
make test-cov   # с отчётом о покрытии
```
