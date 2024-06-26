#!/bin/bash

# Remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -r {} +

# Remove .pyc files
find . -type f -name "*.pyc" -delete

echo "Cleaned up __pycache__ directories and .pyc files."

