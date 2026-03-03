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

# Create necessary directories first
RUN mkdir -p /app/data /app/staticfiles

# Install dependencies
COPY requirements.txt /app/
RUN apk add --no-cache gcc musl-dev linux-headers bash && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create a non-root user
RUN adduser -D -H django && \
    chown -R django:django /app && \
    chmod +x /app/entrypoint.sh

RUN apk del --purge gcc musl-dev linux-headers
# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Run gunicorn
CMD ["sh", "-c", "gunicorn --bind ${HOST}:${PORT} mileage_tracker_config.wsgi:application"]
