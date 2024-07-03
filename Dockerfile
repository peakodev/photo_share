# First stage to generate poetry.lock
FROM python:3.12-slim as builder

# Set the working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy the pyproject.toml file
COPY pyproject.toml /app/

# Generate poetry.lock
RUN poetry lock

# Second stage to build the final image
FROM python:3.12-slim as development

# Set the working directory
WORKDIR /app

# Install necessary dependencies
RUN apt-get update && apt-get install -y postgresql-client make

# Install Poetry
RUN pip install poetry

# Copy the poetry.lock and pyproject.toml files from the builder stage
COPY --from=builder /app/poetry.lock /app/pyproject.toml /app/

# Install dependencies
RUN poetry install --no-root --no-dev

# Copy the rest of the application code
COPY . /app

# Make the entrypoint script executable
RUN chmod +x /app/bin/entrypoint.sh

# Expose the port FastAPI is running on
EXPOSE 8000

# Set the entrypoint to the script
ENTRYPOINT ["/app/bin/entrypoint.sh"]

# Third stage to build the final image for production
# redis server will use the same image as the production for saving resources
FROM development as production

RUN apt-get update && apt-get install -y redis-server

ENTRYPOINT ["sh", "-c", "redis-server & /app/bin/entrypoint.sh"]
