from h2ogpte import H2OGPTE
import os
import psycopg2
from dotenv import load_dotenv
import pandas as pd
import json

current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
load_dotenv(f"{parent_dir}/.env")

client = H2OGPTE(
    address="https://h2ogpte.genai.h2o.ai", api_key=os.getenv("H2O_API_KEY")
)

llm = "gpt-4-1106-preview"

postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_port_no = os.getenv("POSTGRES_PORT_NO")
host = os.getenv("POSTGRES_HOST")
database = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")


def get_db_connection():
    """Get a database connection."""
    return psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=postgres_password,
        port=postgres_port_no,
    )


def load_data():
    """Load and preprocess actual and forecast data."""
    with get_db_connection() as conn:
        products = pd.read_sql_query(
            "SELECT product_id, product_name, category FROM products LIMIT 10", conn
        )
    return products


def create_prompt(name, category):
    """Create a prompt for the Language Model (LLM) based on the given name and category."""
    return f"""
    Generate two catchy versions of the product name and description for a {category} product: 
    Title: '{name}'
    Description: 
    """


def call_llm(prompt):
    """Call the Language Model (LLM) from H2O to generate text based on the provided prompt."""
    chat_session_id = client.create_chat_session_on_default_collection()
    with client.connect(chat_session_id) as session:
        reply = session.query(
            prompt,
            llm=llm,
            llm_args=dict(
                temperature=0.8,
                response_format="json_object",
                guided_json={
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "title1": {"type": "string"},
                        "description1": {"type": "string"},
                        "title2": {"type": "string"},
                        "description2": {"type": "string"},
                    },
                    "required": ["title1", "description1", "title2", "description2"],
                },
            ),
        )
    return reply.content


def generate_product_names(products):
    """Generate catchy product names based on the given product data."""
    for idx, row in products.iterrows():
        prompt = create_prompt(row["product_name"], row["category"])
        generated_text = json.loads(call_llm(prompt))
        products.at[idx, "generated_title1"] = generated_text["title1"]
        products.at[idx, "generated_description1"] = generated_text["description1"]
        products.at[idx, "generated_title2"] = generated_text["title2"]
        products.at[idx, "generated_description2"] = generated_text["description2"]
    return products


def insert_into_db(products_df):
    """Insert the generated product names into a new table in the database."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS generated_products (
                    product_id TEXT,
                    product_name TEXT,
                    category TEXT,
                    generated_title1 TEXT,
                    generated_description1 TEXT,
                    generated_title2 TEXT,
                    generated_description2 TEXT,
                    image_path TEXT
                )
            """
            )
            conn.commit()

            for idx, row in products_df.iterrows():
                image_path = os.path.join(
                    current_dir, "images", f'{row["product_id"]}.jpg'
                )
                cur.execute(
                    """
                    INSERT INTO generated_products (
                        product_id, product_name, category, generated_title1, generated_description1, generated_title2, generated_description2, image_path
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        row["product_id"],
                        row["product_name"],
                        row["category"],
                        row["generated_title1"],
                        row["generated_description1"],
                        row["generated_title2"],
                        row["generated_description2"],
                        image_path,
                    ),
                )
                conn.commit()


def main():
    products = load_data()
    products_df = generate_product_names(products)
    insert_into_db(products_df)
    print("Generated product names and inserted into database")


if __name__ == "__main__":
    main()
