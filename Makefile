SHELL := /bin/bash

.PHONY: setup dev test lint seed ingest detect fetch_gee ingest_gee demo_gee db-up db-down

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
	. .venv/bin/activate && PYTHONPATH=apps/api pytest apps/api/tests pipelines/tests
	cd apps/web && npm run test

lint:
	. .venv/bin/activate && ruff check apps/api
	cd apps/web && npm run lint

seed: db-up
	. .venv/bin/activate && python pipelines/jobs/seed_sample_data.py

ingest:
	. .venv/bin/activate && python pipelines/jobs/ingest_tropomi.py

detect:
	. .venv/bin/activate && if [ -n "$(aoi)" ] && [ -n "$(start)" ] && [ -n "$(end)" ]; then \
		python pipelines/jobs/detect_hotspots.py --ingest-run-id "$(start)_$(end)_$(aoi)"; \
	else \
		python pipelines/jobs/detect_hotspots.py; \
	fi

fetch_gee:
	. .venv/bin/activate && AOI=$${aoi:-permian} START=$${start:-2026-02-01} END=$${end:-2026-02-07} python pipelines/jobs/fetch_gee_ch4.py --aoi "$$AOI" --start "$$START" --end "$$END"

ingest_gee:
	. .venv/bin/activate && AOI=$${aoi:-permian} START=$${start:-2026-02-01} END=$${end:-2026-02-07}; \
	if [ ! -f "pipelines/artifacts/source/gee/$$START_$$END_$$AOI/points.parquet" ]; then \
		python pipelines/jobs/fetch_gee_ch4.py --aoi "$$AOI" --start "$$START" --end "$$END"; \
	fi; \
	python pipelines/jobs/ingest_gee_ch4.py --aoi "$$AOI" --start "$$START" --end "$$END"

demo_gee:
	$(MAKE) fetch_gee aoi=$(aoi) start=$(start) end=$(end)
	$(MAKE) ingest_gee aoi=$(aoi) start=$(start) end=$(end)
	$(MAKE) detect aoi=$(aoi) start=$(start) end=$(end)
