import os
from dotenv import load_dotenv
import sqlalchemy
import pandas as pd

#load from .env file
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)

load_dotenv(f'{parent_dir}/.env')

postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_port_no = os.getenv('POSTGRES_PORT_NO')
host = os.getenv('POSTGRES_HOST')
database = os.getenv('POSTGRES_DB')
user = os.getenv('POSTGRES_USER')

# Create database engine
engine = sqlalchemy.create_engine(f'postgresql://{user}:{postgres_password}@{host}:{postgres_port_no}/{database}')

# function to create 
def create_df(table_name):
    try:
        connection = engine.connect() # Connect to the database
        query = f'''
        SELECT 
            *
        FROM
            {table_name} 
        '''
        # Read data from the database into a DataFrame
        df = pd.read_sql(query, con=connection)
        return df
    except Exception as e:
        print("An error occurred:", e)
        connection.rollback()  # Rollback in case of error
    finally:
        connection.close()  # Close the connection

def create_full_table():
    full_table = create_df('online_sales')
    tables = {'products': 'product_id',
              'users': 'user_id',
              'ratings': 'product_id'
              }
    for key, value in tables:
        df = create_df(key)
        full_table = pd.merge(full_table, df, on=value, how='inner')


