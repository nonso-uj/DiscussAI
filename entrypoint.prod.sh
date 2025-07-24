#!/usr/bin/env bash

# Wait for PostgreSQL to be ready
/wait-for-it.sh $DB_HOST:5432 --timeout=30 --strict -- echo "PostgreSQL is up"


python manage.py collectstatic --noinput

# uses too much memory
# python manage.py migrate --noinput

python -m gunicorn --bind 0.0.0.0:8000 --workers 1 chatrooms.wsgi:application