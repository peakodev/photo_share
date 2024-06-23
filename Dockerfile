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
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy the poetry.lock and pyproject.toml files from the builder stage
COPY --from=builder /app/poetry.lock /app/pyproject.toml /app/

# Install dependencies
RUN poetry install --no-root --no-dev

# Copy the rest of the application code
COPY . /app

# Expose the port FastAPI is running on
EXPOSE 8000

# Command to run the application
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
