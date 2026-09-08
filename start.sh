#!/bin/bash
export PATH="/opt/venv/bin:$PATH"

echo "==> Running database migrations..."
python backend/manage.py migrate --noinput || true

echo "==> Seeding sample Quran data..."
python backend/manage.py import_quran --sample || true

echo "==> Setting up admin account..."
python backend/manage.py setup_admin || true

echo "==> Collecting static assets..."
python backend/manage.py collectstatic --noinput || true

echo "==> Starting Telegram Bot in background..."
if [ -n "$BOT_TOKEN" ]; then
  python -m bot.bot &
fi

echo "==> Starting Gunicorn Web server on port ${PORT:-8000}..."
exec gunicorn backend.quran_tutor.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120