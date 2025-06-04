#!/bin/sh

echo "Waiting for PostgreSQL to be available..."
while ! nc -z dbc 5432; do
  sleep 0.1
done

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate
python manage.py makemigrations inov
python manage.py migrate inov

echo "Seeding data..."
python manage.py seed_extractions  # Call the command without .py

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000