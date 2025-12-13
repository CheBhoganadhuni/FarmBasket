#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Build Tailwind CSS (requires tailwind python package)
python manage.py tailwind install
python manage.py tailwind build

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate
