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

# mkdir htmlcov
HTMLCOV_DIR="htmlcov"

# Create the directory if it does not exist
if [ ! -d "$HTMLCOV_DIR" ]; then
  mkdir -p "$HTMLCOV_DIR"
  echo "Directory $HTMLCOV_DIR created."
else
  echo "Directory $HTMLCOV_DIR already exists."
fi

# Run the tests and prepare allure report
poetry run pytest --alluredir allure-results --cov=app --cov-report=html tests/

chmod -R 755 /app/allure-results

# Start the FastAPI application
exec poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

