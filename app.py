import time 
import numpy as np  
import pandas as pd  
import plotly.express as px  
import streamlit as st  
import psycopg2
from dotenv import load_dotenv
import os

def load_data():
    """Load and preprocess actual and forecast data."""
    # Load actual and forecast data from postgres database
    # Connect to the database
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)

    load_dotenv(f'{parent_dir}/.env')

    postgres_password = os.getenv('POSTGRES_PASSWORD')
    postgres_port_no = os.getenv('POSTGRES_PORT_NO')
    host = os.getenv('POSTGRES_HOST')
    database = os.getenv('POSTGRES_DB')
    user = os.getenv('POSTGRES_USER')
    # connect to db
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=postgres_password,
        port=postgres_port_no
    )
    
    print("Connected to database")
    # Get products table 
    products = pd.read_sql_query("SELECT * FROM products", conn)

    # Get actual sales data
    actual_data = pd.read_sql_query("""
                                    SELECT date, product_id, SUM("Quantity") AS sales
                                    FROM online_sales 
                                    GROUP BY date, product_id
                                    ORDER BY product_id, date""", conn)
    forecast_data = pd.read_csv('demand_forecast/forecast.csv')
    return actual_data, forecast_data, products

def filter_data_by_product(actual_data, forecast_data, product):
    """Filter actual and forecast data by selected product."""
    actual_product_data = actual_data[actual_data["product_id"] == product]
    forecast_product_data = forecast_data[forecast_data["product"] == product]
    
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

def load_product_details(products, product):
    """Load product details from products.csv."""
    # Add USD infront of the price
    products["actual_price"] = "USD " + products["actual_price"].astype(str) 
    products["discounted_price"] = "USD "+ products["discounted_price"].astype(str) 
    
    product_details = products[products["product_name"] == product]
    
    product_name = product_details["product_name"].values[0]
    product_category = product_details["category"].values[0]
    product_price = product_details["actual_price"].values[0]
    product_discounted = product_details["discounted_price"].values[0]
    
    return product_name, product_category, product_price, product_discounted

def display_product_details(tab,product_name, product_category, product_price, product_discounted):
    """Display product details on Streamlit."""
    tab.write(f"**🛍️ Product Name:** {product_name}")
    tab.write(f"**🛒 Product Category:** {product_category}")
    tab.write(f"**💰 Product Price:** {product_price}")
    tab.write(f"**💲 Product Discounted Price:** {product_discounted}")

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
        product_name, product_category, product_price, product_discounted = load_product_details(products, product)
        display_product_details(tab1, product_name, product_category, product_price, product_discounted)
    else:
        tab1.write("No products found.")

def main():
    """Main function to run the Streamlit app."""
    st.title("Passion8: E-commerce Performance Analysis and Optimization📈")

    tab1, tab2 = st.tabs(["📈 Demand Forecast Optimization", "🗃 Sentiment Analysis"])
    
    # Load data
    actual_data, forecast_data, products = load_data()

    # Display content for tab1
    display_tab1(tab1, actual_data, forecast_data, products)
    
    
if __name__ == "__main__":
    main()