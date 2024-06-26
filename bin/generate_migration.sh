#!/bin/bash

docker-compose exec fastapi-app poetry run alembic revision --autogenerate -m "$1"

