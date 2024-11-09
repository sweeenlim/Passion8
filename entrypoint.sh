#!/bin/sh

# Run the database initialization script
python data/db_init.py

# Run the Streamlit application
exec streamlit run Hello.py