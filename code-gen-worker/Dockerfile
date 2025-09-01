FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The command to start the Celery worker
CMD ["celery", "-A", "tasks.celery_app", "worker", "--loglevel=info"]