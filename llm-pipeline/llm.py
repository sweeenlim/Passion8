from h2ogpte import H2OGPTE
import os
import psycopg2
from dotenv import load_dotenv
import pandas as pd
import json

client = H2OGPTE(
    address='https://h2ogpte.genai.h2o.ai',
    api_key='sk-ptd42vP3XfbkjgOIVsqMYMXOxZ5l80MwV0qkRt3ANtUWOsMJ',
)

llm = "gpt-4-1106-preview"
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
load_dotenv(f'{parent_dir}/.env')

postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_port_no = os.getenv('POSTGRES_PORT_NO')
host = os.getenv('POSTGRES_HOST')
database = os.getenv('POSTGRES_DB')
user = os.getenv('POSTGRES_USER')


def load_data():
    """Load and preprocess actual and forecast data."""
    # Load actual and forecast data from postgres database
    # Connect to the database

    # connect to db
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=postgres_password,
        port=postgres_port_no
    )
    #get products table
    products = pd.read_sql_query("SELECT product_id, product_name, category FROM products LIMIT 10", conn)
    conn.close()
    return products

def create_prompt(name,category):
    """
    Creates a prompt for the Language Model (LLM) based on the given name and category.

    Args:
        name (str): The name of the product.
        category (str): The category of the product.

    Returns:
        str: The generated prompt based on the given name and category.
    """
    prompt = f'''
    Generate two catchy versions of the product name and description for a {category} product: 
    Title: '{name}'
    Description: 
    '''
    return prompt

def call_llm(prompt):
    """
    Calls the Language Model (LLM) from H2O to generate text based on the provided prompt.

    Args:
        prompt (str): The prompt to be used for text generation.

    Returns:
        str: The generated text based on the given prompt.
    """
    chat_session_id = client.create_chat_session_on_default_collection()
    with client.connect(chat_session_id) as session:
        reply = session.query(
            prompt,llm=llm,
            llm_args=dict(
            temperature=0.8,
            response_format='json_object',
            guided_json={
                '$schema': 'http://json-schema.org/draft-07/schema#',
                'type': 'object',
                'properties': {'title1': {'type': 'string'}, 'description1': {'type': 'string'}, 'title2': {'type': 'string'}, 'description2': {'type': 'string'}},
                'required': [
                    'title1',
                    'description1',
                    'title2',
                    'description2',
                ],
            },
        ),
        )
    answer = reply.content
    return answer

def generate_product_names(products):
    """
    Generates catchy product names based on the given product data.

    Args:
        products (pd.DataFrame): The product data containing product id, names and categories.

    Returns:
        pd.DataFrame: The product data with additional columns for the generated product names.
    """
    for idx, row in products.iterrows():
        name = row['product_name']
        category = row['category']
        id = row['product_id']
        prompt = create_prompt(name, category)
        generated_text = call_llm(prompt) # is json object
        #print(generated_text)
        # product_names.append(generated_text)
        # Add the 3 variations of generated product names to the products DataFrame
        generated_text= json.loads(generated_text)
        print(generated_text)
        products.loc[idx, 'product_id'] = id 
        products.loc[idx, 'generated_title1'] = generated_text['title1']
        products.loc[idx, 'generated_description1'] = generated_text['description1']
        products.loc[idx, 'generated_title2'] = generated_text['title2']
        products.loc[idx, 'generated_description2'] = generated_text['description2']
    
    return products

def insert_into_db(products_df):
    """
    Inserts the generated product names into a new table in the database.

    Args:
        products_df (pd.DataFrame): The product data containing the generated product names.
    """
    # connect to db
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=postgres_password,
        port=postgres_port_no
    )
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS generated_products (product_id TEXT, product_name TEXT, category TEXT, generated_title1 TEXT, generated_description1 TEXT, generated_title2 TEXT, generated_description2 TEXT)")
    conn.commit()

    for idx, row in products_df.iterrows():
        cur.execute("INSERT INTO generated_products (product_id, product_name, category, generated_title1, generated_description1, generated_title2, generated_description2) VALUES (%s, %s, %s, %s, %s, %s, %s)", (row['product_id'], row['product_name'], row['category'], row['generated_title1'], row['generated_description1'], row['generated_title2'], row['generated_description2']))
        conn.commit()
    cur.close()
    conn.close()
    

def main():
    products = load_data()
    products_df = generate_product_names(products)
    insert_into_db(products_df)
    print("Generated product names and inserted into database")

    
    

if __name__ == "__main__":
    main()