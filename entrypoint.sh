#!/bin/bash
set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files (optional, can be done in build)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
exec "$@"
