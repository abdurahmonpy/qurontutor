#!/bin/bash
set -e

echo "==> Running database migrations..."
python backend/manage.py migrate --noinput

echo "==> Seeding sample Quran data..."
python backend/manage.py import_quran --sample || true

echo "==> Collecting static assets..."
python backend/manage.py collectstatic --noinput

echo "==> Starting Telegram Bot in background..."
python -m bot.bot &

echo "==> Starting Gunicorn Web server on port ${PORT:-8000}..."
exec gunicorn --chdir backend quran_tutor.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120