FROM python:3.12-slim

# Python runtime settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies at build time
COPY requirements.txt /app/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /app/requirements.txt

# Copy application code and migrations
COPY app /app/app
COPY start.py /app/start.py
COPY scripts/create_api_client.py /app/scripts/create_api_client.py
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic

# Copy helper scripts to root directory and set permissions
COPY entrypoint.sh wait-for-postgres.sh /
RUN chmod +x /entrypoint.sh /wait-for-postgres.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "start.py"]
