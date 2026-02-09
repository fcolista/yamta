#!/bin/bash
set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if env vars are set
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL || echo "Superuser already exists or could not be created."
fi


# Collect static files (optional, can be done in build)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
exec "$@"
