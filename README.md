# PhotoShare

## Description

The project is structured as follows:

- `app/`: fastapi project folder
- `bin/`: additional scripts
- `app/conf/config.py`: class with ability to get .env variables using pydantic_settings
- `app/models/`: folder with db connections and models
- `app/routes/`: folder with routes like posts, auth, comments
- `app/repository/`: folder with repositories scripts lilke posts, comments, tags
- `app/schemas/`: folder with pydentic schemas
- `src/services/`: folder with services (email, auth, qrcode_gen, cloudinary)
- `main.py`: fastapi entrypoint
- `tests/`: folder with tests
- `bin/cleanup.sh`: Cleaned up __pycache__ directories and .pyc files.

## Running the application in Docker

Run docker compose

```bash
docker-compose up -d
```

Rebuild poetry libs

```bash
docker-compose up --build
```

## Tests

@TODO: will run in container

```bash
docker-compose run test
```