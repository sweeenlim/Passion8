import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
import os
import psycopg2
from sqlalchemy import create_engine

# Load environment variables
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
load_dotenv(f'{parent_dir}/.env')

postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_port_no = os.getenv('POSTGRES_PORT_NO')
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

def load_data_tab3():
    """Load the data for supply chain efficiency analysis."""
    with get_db_connection() as conn:
        # Load the required tables for analysis
        shipping_status_df = pd.read_sql_query("SELECT * FROM shipping_status", conn)
        products_df = pd.read_sql_query("SELECT * FROM products", conn)
    return shipping_status_df, products_df

def preprocess_data(shipping_status_df):
    """Calculate the average days taken between each step in the order fulfillment process."""
    successful_orders = shipping_status_df.groupby('shipping_id').filter(lambda x: 
        list(x['status']) == ["Pending", "Packed", "At logistics facility", "Shipping", "Delivered to buyer"]
    )
    successful_orders['update_date'] = pd.to_datetime(successful_orders['update_date'])
    successful_orders = successful_orders.sort_values(['shipping_id', 'update_date'])
    successful_orders['days_from_previous'] = successful_orders.groupby('shipping_id')['update_date'].diff().dt.days
    duration_df = successful_orders.groupby(['status', 'fulfilment'])['days_from_previous'].mean().reset_index()
    return duration_df

def plot_proportion_of_days(duration_df):
    """Plot the average days taken between steps in the order fulfillment process by status and fulfilment."""
    fig = px.bar(duration_df, 
                 x='status', 
                 y='days_from_previous', 
                 color='fulfilment', 
                 title='Proportion of Days Taken for Each Step in Order Fulfillment Process by Condition',
                 labels={'days_from_previous': 'Average Days Taken', 'status': 'Order Status'},
                 barmode='group')
    return fig

def top_10_product_performance(shipping_status_df, products_df):
    """Get the top 10 products with the most returns or cancellations."""
    returned_df = shipping_status_df[shipping_status_df['status'].isin(['Returned', 'Cancelled'])]
    product_counts_df = returned_df['product_id'].value_counts().reset_index()
    product_counts_df.columns = ['product_id', 'count']
    product_counts_df = product_counts_df.sort_values(by='count', ascending=False)
    product_counts_df = pd.merge(product_counts_df, products_df, how='left', on='product_id')
    top_10_df = product_counts_df.nlargest(10, 'count')
    return top_10_df

def display_tab3(tab3, data_tab3):
    """Display content for tab3."""
    shipping_status_df, products_df = data_tab3
    
    # Create a select box to choose between two views
    view_option = tab3.selectbox(
        "Select View",
        ["Top 10 suppliers with poor product performance", "Days Taken for Each Step in Order Fulfillment Process by Condition"]
    )

    if view_option == "Top 10 suppliers with poor product performance":
        tab3.subheader("Top 10 Frequently Returned or Cancelled Products")
        top_10_df = top_10_product_performance(shipping_status_df, products_df)
        tab3.dataframe(top_10_df)  # Display the table in Streamlit
    
    elif view_option == "Days Taken for Each Step in Order Fulfillment Process by Condition":
        tab3.subheader("Proportion of Days Taken for Each Step in Order Fulfillment Process")
        duration_df = preprocess_data(shipping_status_df)
        fig = plot_proportion_of_days(duration_df)
        tab3.plotly_chart(fig)
