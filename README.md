# PhotoShare

## Description

The project is structured as follows:

- `app/`: fastapi project folder
- `app/conf/config.py`: class with ability to get .env variables using pydantic_settings
- `app/database/`: folder with db connections and models
- `app/routes/`: folder with routes for auth and contacts
- `main.py`: fastapi entrypoint
- `bin/cleanup.sh`: Cleaned up __pycache__ directories and .pyc files.

## Prepare env

### Install libs 

```bash
poetry install
```

### Running the postgres in Docker container

Run docker compose

```bash
docker-compose up -d
```

Run server for testing

```bash
uvicorn main:app --host localhost --port 8008 --reload
```