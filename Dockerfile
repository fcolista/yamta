FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STATIC_ROOT=/app/staticfiles

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Create a non-root user
RUN adduser --disabled-password --no-create-home django && \
    chown -R django:django /app

# Copy entrypoint script
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "mileage_tracker_config.wsgi:application"]
