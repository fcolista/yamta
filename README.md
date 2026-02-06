# Mileage Tracker

A clean, modern web application for tracking vehicle mileage and fuel costs. Built with Django and styled with Tailwind CSS.

## Features & Usage

### 1. Dashboard
The main landing page provides a quick overview of your current month's activity:
- **Total Mileage**: Sum of distances for the current month.
- **Quick Links**: Fast access to add a journey or view reports.
- **Recent Activity**: A glance at the latest logged trips.

### 2. Add Journey
Log a new trip with ease:
- **Date**: Defaults to today.
- **Distance**: Enter the trip distance (km/miles).
- **Reason**: Classify the trip (e.g., Business, Personal, Medical).
- **Fuel Type**: Auto-filled from your settings, but customizable per trip.
- **Cost**: Calculated automatically based on distance and fuel rates, or manually overrideable.

### 3. Edit Fuel Rates
Manage your fuel reimbursement rates:
- Update per-unit costs for different fuel types (e.g., Petrol, Diesel, Electric).
- These rates are used to automatically calculate trip costs.

### 4. History
View and filter your entire trip log:
- **Filters**: Filter by Month and Year.
- **Details**: See distance, date, reason, and cost for every trip.
- **Edit**: Click any trip to edit its details.

### 5. Settings
Configure global application preferences:
- **Default Fuel Type**: Set your preferred fuel type for quicker data entry.
- **Currency**: Set your local currency symbol (e.g., $, €, £).

### 6. Reports
Visualize your data:
- **Cost Distribution**: View a breakdown of costs by fuel type.

---

## Environment & Configuration

This project is containerized using Docker and Docker Compose for easy deployment.

### Quick Start (Production)

1.  **Build and Run**:
    ```bash
    docker-compose up --build -d
    ```
2.  **Access**:
    Open [http://localhost:8000](http://localhost:8000) in your browser.

The database will be automatically created and migrated on first launch.

### Environment Variables

The application is configured via environment variables defined in `docker-compose.yml`.

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `PROD` | **Critical**. Set to `True` for production mode. Enables persistent database storage in `data/` volume. | `True` |
| `DEBUG` | Django debug mode. **Set to `False` in production.** | `False` |
| `DJANGO_SECRET_KEY` | Secret cryptographic key for Django. **Change this to a random string in production.** | `production_secret_key_change_me` |
| `ALLOWED_HOSTS` | Comma-separated list of valid hostnames/IPs that can serve the app. | `localhost,127.0.0.1` |

### Volumes and Persistence

Data is persisted using Docker named volumes. You can destroy and recreate containers without losing data.

- **`data`**: Maps to `/app/data` inside the container. Stores the SQLite database (`db.sqlite3`) when `PROD=True`.
- **`static_volume`**: Maps to `/app/staticfiles`. Stores collected static files (CSS, JS) for efficient serving (configured for Nginx/Web Server if needed).

### Development Mode

To run locally without Docker for development:

1.  Create a virtual environment: `python -m venv venv`
2.  Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
3.  Install deps: `pip install -r requirements.txt`
4.  Run migrations: `python manage.py migrate`
5.  Run server: `python manage.py runserver`
