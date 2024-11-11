FROM python:3.12.4-slim

# Install PostgreSQL client and development libraries for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip3 install --default-timeout=100 -r requirements.txt

EXPOSE 8501

# Healthcheck to ensure Streamlit is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Start Streamlit
CMD ["streamlit", "run", "Hello.py"]