FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --no-cache-dir --requirement /tmp/requirements.txt
COPY . .
RUN mkdir -p /app/staticfiles/assets
RUN mkdir -p /app/staticfiles/bundles
RUN python3 manage.py collectstatic --noinput