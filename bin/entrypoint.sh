#!/bin/sh
# entrypoint.sh

set -e

# Wait for PostgreSQL to be ready
until pg_isready -h "$POSTGRES_HOST" -U "$POSTGRES_USER"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

# Run Alembic migrations
poetry run alembic upgrade head

# Navigate to the docs directory and run `make html`
cd /app/docs && poetry run make html && cd ..

chmod -R 755 /app/docs

# Run the tests and prepare allure report
poetry run pytest --alluredir allure-results

chmod -R 755 /app/allure-results

# Start the FastAPI application
exec poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

