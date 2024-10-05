import time 
import numpy as np  
import pandas as pd  
import plotly.express as px  
import streamlit as st  
import psycopg2

def load_data():
    """Load and preprocess actual and forecast data."""
    # Load actual and forecast data from postgres database
    # Connect to the database
    conn = psycopg2.connect(
        host="localhost",
        database="dsa3101",
        user="postgres",
        password=""
    )
    # Get products table
    products = pd.read_sql_query("SELECT * FROM products", conn)

    # Get actual sales data
    actual_data = pd.read_sql_query("""
                                    SELECT date, product_id, SUM("Quantity") AS sales
                                    FROM online_sales 
                                    GROUP BY date, product_id
                                    ORDER BY product_id, date""", conn)
    forecast_data = pd.read_csv("/Users/user/Passion8/demand_forecast/forecast.csv")

    
    
    
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
    # Add USD behind the price
    products["actual_price"] = products["actual_price"].astype(str) + " USD"
    products["discounted_price"] = products["discounted_price"].astype(str) + " USD"
    
    product_details = products[products["product_name"] == product]
    
    product_name = product_details["product_name"].values[0]
    product_category = product_details["category"].values[0]
    product_price = product_details["actual_price"].values[0]
    product_discounted = product_details["discounted_price"].values[0]
    
    return product_name, product_category, product_price, product_discounted

def display_product_details(product_name, product_category, product_price, product_discounted):
    """Display product details on Streamlit."""
    st.write(f"**🛍️ Product Name:** {product_name}")
    st.write(f"**🛒 Product Category:** {product_category}")
    st.write(f"**💰 Product Price:** {product_price}")
    st.write(f"**💲 Product Discounted Price:** {product_discounted}")

def main():
    """Main function to run the Streamlit app."""
    st.title("Demand Forecasting Dashboard📈")
    
    # Load data
    actual_data, forecast_data, products = load_data()
    
    # Top level filters for product from product details
    # Get the products that exist in both actual and products data
    products = products[products["product_id"].isin(actual_data["product_id"].unique())]
    product = st.selectbox("Select a product", products["product_name"].unique())
    product_id = products[products["product_name"] == product]["product_id"].values[0]
    print(product_id)
    # Filter data by selected product
    actual_product_data, forecast_product_data = filter_data_by_product(actual_data, forecast_data, product_id)
    
    # Create and display line chart
    fig = create_line_chart(actual_product_data, forecast_product_data)
    st.plotly_chart(fig)
    
    # Load and display product details
    product_name, product_category, product_price, product_cost = load_product_details(products,product)
    display_product_details(product_name, product_category, product_price, product_cost)

if __name__ == "__main__":
    main()