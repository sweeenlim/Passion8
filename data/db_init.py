import os
import pandas as pd
from sqlalchemy import create_engine, inspect
import logging

logging.basicConfig(level=logging.INFO)


# Read environment variables
def get_db_credentials():
    user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("POSTGRES_DB")
    return user, postgres_password, database


def create_db_engine(user, postgres_password, database):
    # Create the database engine
    engine = create_engine(
        f"postgresql://{user}:{postgres_password}@db:5432/{database}"
    )
    return engine


def connect_to_db(engine):
    # Retry mechanism for connecting to the database
    while True:
        try:
            connection = engine.connect()
            if connection:
                return connection
        except Exception as e:
            print(f"Retrying to connect to the database: {e}")


def read_csv_files():
    paths = {
        "products": "data/products.csv",
        "ratings": "data/ratings.csv",
        "users": ["data/users.csv", "data/online_sales_users.csv"],
        "user_behaviour": "data/user_behaviour.csv",
        "online_sales": "data/online_sales_edited.csv",
        "shipping_status": "data/shipping_status.csv",
        "shipping_history": "data/shipping_history.csv",
    }
    dataframes = {}
    for name, path in paths.items():
        if isinstance(path, list):
            # Concatenate multiple CSV files into one DataFrame
            df_list = [pd.read_csv(p) for p in path]
            dataframes[name] = pd.concat(df_list, ignore_index=True)
        else:
            dataframes[name] = pd.read_csv(path)
    return dataframes


def convert_date_columns(dataframes):
    date_columns = {
        "online_sales": ["date"],
        "shipping_history": ["date", "update_date"],
        "shipping_status": ["date", "estimated_delivery_date"],
    }
    for df_name, columns in date_columns.items():
        for column in columns:
            dataframes[df_name][column] = pd.to_datetime(
                dataframes[df_name][column], format="%Y-%m-%d", errors="raise"
            ).dt.date


def insert_data_to_db(dataframes, engine):
    # Insert data into the database
    for table_name, df in dataframes.items():
        df.to_sql(table_name, engine, if_exists="append", index=False)


def main():
    user, postgres_password, database = get_db_credentials()
    engine = create_db_engine(user, postgres_password, database)
    connect_to_db(engine)

    dataframes = read_csv_files()
    convert_date_columns(dataframes)
    insert_data_to_db(dataframes, engine)

    print("Tables created successfully")


if __name__ == "__main__":
    main()
