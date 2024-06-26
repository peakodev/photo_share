#!/bin/bash

# Build the Docker image
docker build -t fastapi-app .

# Run the container to generate poetry.lock
docker run --rm -v $(pwd):/app fastapi-app poetry lock

# Add and commit the poetry.lock file to Git
git add poetry.lock
git commit -m "Add/update poetry.lock"
git push origin main


