#!/bin/sh
set -e

cd /app

# Optionally install dependencies at runtime (default: skip)
if [ "${INSTALL_DEPS_ON_START:-0}" = "1" ]; then
  echo "INSTALL_DEPS_ON_START=1 -> Installing Python dependencies..."
  pip install -r requirements.txt
fi

# Optionally run database migrations
if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  echo "RUN_MIGRATIONS=1 -> Running database migrations..."
  alembic upgrade head
fi

echo "Starting the app..."
exec "$@"