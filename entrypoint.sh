#!/bin/bash
set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if env vars are set
# Create or update superuser
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating/Updating superuser..."
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if username and password:
    if User.objects.filter(username=username).exists():
        print(f"Updating superuser {username}")
        user = User.objects.get(username=username)
        user.set_password(password)
        if email:
            user.email = email
        user.is_superuser = True
        user.is_staff = True
        user.save()
    else:
        print(f"Creating superuser {username}")
        User.objects.create_superuser(username=username, email=email, password=password)
EOF
fi


# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
exec "$@"
