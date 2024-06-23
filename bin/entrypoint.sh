#!/bin/sh
# entrypoint.sh

set -e

# Wait for PostgreSQL to be ready
until pg_isready -h "postgres" -U "$POSTGRES_USER"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

# Run Alembic migrations
poetry run alembic upgrade head

# Start the FastAPI application
exec poetry run uvicorn main:app --host 0.0.0.0 --port 8000
