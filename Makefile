SHELL := /bin/bash

.PHONY: setup dev test lint seed db-up db-down

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -U pip && pip install -r apps/api/requirements-dev.txt
	cd apps/web && npm install

ensure-env:
	@if [ ! -f .env ]; then cp .env.example .env; fi

db-up: ensure-env
	docker compose up -d db

db-down:
	docker compose down

dev: ensure-env
	docker compose up --build

test:
	. .venv/bin/activate && PYTHONPATH=apps/api pytest apps/api/tests
	cd apps/web && npm run test

lint:
	. .venv/bin/activate && ruff check apps/api
	cd apps/web && npm run lint

seed: db-up
	. .venv/bin/activate && python pipelines/jobs/seed_sample_data.py
