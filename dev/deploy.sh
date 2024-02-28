#!/bin/bash

echo 'stop'
docker-compose down --rmi local

echo 'start'
docker-compose up --build -d

echo 'migrate'
docker-compose exec backend python manage.py migrate --noinput

echo 'collectstatic'
docker-compose exec backend python manage.py collectstatic --noinput

