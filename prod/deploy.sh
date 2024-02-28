#!/bin/bash

set -e

echo 'start deploy'

echo 'git pull'
git pull

echo 'stop'
docker-compose down --rmi local

echo 'start'
docker-compose up --build -d

echo 'migrate'
docker-compose exec backend python manage.py migrate --noinput

echo 'collectstatic'
docker-compose exec backend python manage.py collectstatic --noinput

echo 'reload nginx daemon'
systemctl reload nginx

source /opt/star-burger/.env

echo 'rollbar info deploy'

COMMIT_HASH=$(git rev-parse HEAD)
curl -H "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" \
     -H "Content-Type: application/json" \
     -X POST 'https://api.rollbar.com/api/1/deploy' \
     -d "{\"environment\": \"production\", \"revision\": \"$COMMIT_HASH\", \"status\": \"succeeded\", \"rollbar_username\": \"$ROLLBAR_USERNAME\"}"

echo 'end deploy'