UV ?= uv
BACKEND_DIR := backend
FRONTEND_DIR := frontend

.PHONY: help install install-backend install-frontend dev-backend dev-frontend lint-frontend build-frontend run-backend-prod clean lock-backend

help:
	@echo "Цели:"
	@echo "  make install            — зависимости: uv sync в backend, npm во frontend"
	@echo "  make lock-backend       — обновить backend/uv.lock"
	@echo "  make dev-backend        — API http://127.0.0.1:8000"
	@echo "  make dev-frontend       — UI http://127.0.0.1:8080"
	@echo "  make build-frontend     — сборка frontend/build"
	@echo "  make run-backend-prod   — uvicorn без reload"
	@echo "  make lint-frontend      — eslint"
	@echo "  make clean              — .venv, node_modules, tasks.db"

install: install-backend install-frontend

install-backend:
	cd $(BACKEND_DIR) && $(UV) sync

lock-backend:
	cd $(BACKEND_DIR) && $(UV) lock

install-frontend:
	cd $(FRONTEND_DIR) && npm install

dev-backend:
	cd $(BACKEND_DIR) && $(UV) run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

dev-frontend:
	cd $(FRONTEND_DIR) && npm run start

build-frontend:
	cd $(FRONTEND_DIR) && npm run build

run-backend-prod:
	cd $(BACKEND_DIR) && $(UV) run uvicorn app.main:app --host 127.0.0.1 --port 8000

lint-frontend:
	cd $(FRONTEND_DIR) && npm run lint

clean:
	rm -rf $(BACKEND_DIR)/.venv $(FRONTEND_DIR)/node_modules $(BACKEND_DIR)/tasks.db
