#!/bin/bash

alembic upgrade head
python -m src.auth.certs.create_certs
gunicorn src.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
echo "Приложение успешно запущенно!"