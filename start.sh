#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until nc -z $DB_HOST 5432; do
  sleep 1
done

# Run database migrations
echo "Running migrations..."
python manage.py migrate

# Start Gunicorn
echo "Starting server..."
gunicorn your_project.wsgi:application --bind 0.0.0.0:8000 --workers 4