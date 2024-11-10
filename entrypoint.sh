#!/bin/sh

#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for the PostgreSQL database to be ready..."
until pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Database is ready, initialize it if needed
echo "Database is ready. Running initialization script (if any)..."

# Start Streamlit application
echo "Starting Streamlit..."
exec streamlit run Hello.py
