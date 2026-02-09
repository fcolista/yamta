FROM python:3.12-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STATIC_ROOT=/app/staticfiles
ENV HOST=0.0.0.0
ENV PORT=8000
ENV ALLOWED_HOSTS=127.0.0.1,localhost
ENV CSRF_TRUSTED_ORIGINS=http://localhost:8000

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
# Install build deps and bash (for entrypoint)
RUN apk add --no-cache gcc musl-dev linux-headers bash && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Create a non-root user
RUN adduser -D -H django

# Copy entrypoint script
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Create data directory and chown all
RUN mkdir -p /app/data /app/staticfiles && \
    chown -R django:django /app

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Run gunicorn
CMD ["sh", "-c", "gunicorn --bind ${HOST}:${PORT} mileage_tracker_config.wsgi:application"]
