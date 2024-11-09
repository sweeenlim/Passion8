FROM python:3.12.4-slim

# Install PostgreSQL client and development libraries for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip3 install --default-timeout=100 -r requirements.txt

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Set the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]