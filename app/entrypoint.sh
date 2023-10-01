#!/bin/sh

poetry run alembic upgrade head
poetry run uvicorn main:app  --proxy-headers --host 0.0.0.0 --port 8000
