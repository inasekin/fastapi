# Задание по FastAPI

[![Maintainability](https://qlty.sh/gh/inasekin/projects/fastapi/maintainability.svg)](https://qlty.sh/gh/inasekin/projects/fastapi)

## Требования

- **GNU Make** — на macOS и Linux обычно уже есть; в Windows — [через Chocolatey](https://community.chocolatey.org/packages/make)
- [uv](https://docs.astral.sh/uv/) (Python 3.11+)
- Node.js 16+ (фронтенд)

## Быстрый старт

```bash
make install
```

В двух терминалах:

```bash
make dev-backend    # API: http://127.0.0.1:8000
make dev-frontend   # UI:  http://127.0.0.1:8080
```

## Запуск тестов

```bash
make test
```

Покрытие и отчеты

```bash
make test-cov  
```
```bash
make test-html
```
