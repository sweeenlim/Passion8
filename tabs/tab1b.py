import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
import os
import psycopg2

# Load environment variables
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
load_dotenv(f'{parent_dir}/.env')

postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_port_no = os.getenv('POSTGRES_PORT')
host = os.getenv('POSTGRES_HOST')
database = os.getenv('POSTGRES_DB')
user = os.getenv('POSTGRES_USER')

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
        print("Connected to database")
        # Get products table 
        products = pd.read_sql_query("SELECT * FROM products", conn)

        # Get actual sales data
        actual_data = pd.read_sql_query("""
                                        SELECT date, product_id, SUM(quantity) AS sales
                                        FROM online_sales 
                                        GROUP BY date, product_id
                                        ORDER BY product_id, date""", conn)
    forecast_data = pd.read_csv('demand_forecast/forecast.csv')
    return actual_data, forecast_data, products

def filter_data_by_product(actual_data, forecast_data, product_id):
    """Filter actual and forecast data by selected product."""
    actual_product_data = actual_data[actual_data["product_id"] == product_id]
    forecast_product_data = forecast_data[forecast_data["product"] == product_id]
    return actual_product_data, forecast_product_data

def create_line_chart(actual_product_data, forecast_product_data):
    """Create a line chart for actual and forecast data."""
    actual_product_data["date"] = pd.to_datetime(actual_product_data["date"])
    forecast_product_data["date"] = pd.to_datetime(forecast_product_data["date"])
    
    actual_product_data['type'] = 'actual'
    forecast_product_data['type'] = 'forecast'
    
    df = pd.concat([actual_product_data, forecast_product_data])
    fig = px.line(df, x="date", y="sales", color="type", title="Actual vs Forecast")
    
    return fig

def load_product_details(products, product_id):
    """Load product details from products.csv."""
    # Add USD in front of the price
    products["actual_price"] = "USD " + products["actual_price"].astype(str) 
    products["discounted_price"] = "USD " + products["discounted_price"].astype(str) 


    product_details = products[products["product_id"] == product_id]
    product_details = product_details[["product_name", "category", "actual_price", "discounted_price"]]
    # Rename columns to more readable names
    product_details = product_details.rename(columns={
        "product_name": "Product Name",
        "category": "Category",
        "actual_price": "Actual Price",
        "discounted_price": "Discounted Price"
    })
    product_details = product_details.T
    print(product_details)
    product_details.columns = ["Details"]
    return product_details

def display_product_details(tab, product_details):
    """Display product details on Streamlit."""
    tab.dataframe(product_details,use_container_width=True)

def display_tab1(tab1, actual_data, forecast_data, products):
    """Display content for tab1."""
   # Extract the first part of the category before '|'
    products['category'] = products['category'].apply(lambda x: x.split('|')[0])
    
    # Top level filters for product from product details
    # Get the products that exist in both actual and products data
    products = products[products["product_id"].isin(actual_data["product_id"].unique())]
    
    # Select a category
    categories = products['category'].unique()
    selected_category = tab1.selectbox("Select a category", categories)
    
    # Filter products by selected category
    filtered_products = products[products['category'] == selected_category]
    
    if not filtered_products.empty:
        product = tab1.selectbox("Select a product", filtered_products["product_name"].values)
        product_id = filtered_products[filtered_products["product_name"] == product]["product_id"].values[0]
        
        # Filter data by selected product
        actual_product_data, forecast_product_data = filter_data_by_product(actual_data, forecast_data, product_id)
        
        # Create and display line chart
        fig = create_line_chart(actual_product_data, forecast_product_data)
        tab1.plotly_chart(fig)
        
        # Load and display product details

        product_details = load_product_details(products, product_id)
        display_product_details(tab1, product_details)
    else:
        tab1.write("No products found.")