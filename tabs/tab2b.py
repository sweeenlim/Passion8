import pandas as pd
import streamlit as st
from dotenv import load_dotenv

def load_data_tab2():
    return pd.read_csv("pricing strategies/forecast_with_ped.csv")

def expected_revenue(price, discount, forecast_demand, ped):
    p_new = price * (1 - discount)
    d_new = forecast_demand * (p_new / price) ** ped
    return d_new, p_new, p_new * d_new

def display_product_details(tab, product_name, product_base_category, PED, 
                            original_price, forecast_demand, revenue,
                            discounted_price, new_forecast_demand, new_revenue):
    """Display product details on Streamlit."""
    tab.markdown(f"""
    <div style="font-size:16px;">
        <strong>🛍️ Product Name:</strong> {product_name} <br>
        <strong>📦 Product Base Category:</strong> {product_base_category} <br>
        <strong>💰 Price Elasticity of Demand:</strong> {round(PED, 3)} <br>
    </div>
    """, unsafe_allow_html=True)

    # Add a gap between the price elasticity and the columns
    tab.markdown("<br>", unsafe_allow_html=True)  # Add a line break for spacing

    # Create two columns for pricing and demand details
    col1, col2 = tab.columns([1, 1])  # Two equal columns

    # Populate the first column with original price, forecast demand, and revenue
    with col1:
        col1.markdown(f"""
        <div style="font-size:16px;">
            <strong>📊 Original Price:</strong> ${round(original_price, 3):.3f} <br>
            <strong>🔮 Forecast Demand:</strong> {round(forecast_demand, 3)} <br>
            <strong>💵 Revenue:</strong> ${round(revenue, 3):.3f} <br>
        </div>
        """, unsafe_allow_html=True)

    # Populate the second column with discounted price, new forecast demand, and new revenue
    with col2:
        col2.markdown(f"""
        <div style="font-size:16px;">
            <strong>🔖 Discounted Price:</strong> ${round(discounted_price, 3):.3f} <br>
            <strong>📈 New Forecast Demand after Discount:</strong> {round(new_forecast_demand, 3)} <br>
            <strong>💸 New Revenue:</strong> ${round(new_revenue, 3):.3f} <br>
        </div>
        """, unsafe_allow_html=True)

    # Calculate the revenue difference and round it
    revenue_difference = round(new_revenue - revenue, 3)

    # Display the revenue difference below the two columns
    tab.markdown(f"""
    <div style="text-align:center; font-size:16px; margin-top: 20px;">
        <strong>📊 Revenue Difference:</strong> ${revenue_difference:.3f} <br>
    </div>
    """, unsafe_allow_html=True)

def display_tab2(tab2, data):
    base_categories = data['base_cat'].unique()
    selected_category = tab2.selectbox("Select a category", base_categories)
    
    # Filter products by selected category
    filtered_products = data[data['base_cat'] == selected_category]['product_name']

    months = ["January", "February", "March"]
    
    if not filtered_products.empty:
        selected_product = tab2.selectbox("Select a product", filtered_products)
        selected_month = tab2.selectbox("Select a month", months)
        selected_discount = tab2.slider(
            "Select your discount percentage between -50% and 100%", 
            min_value=-50, 
            max_value=100, 
            value=0,  # Start at 0
            step=1
        )

        chosen = data[(data['month'] == selected_month) & (data['product_name'] == selected_product)]
        original_demand = chosen['sales'].values[0]
        original_price = chosen['actual_price'].values[0]
        ped = chosen['PED'].values[0]

        new_demand, new_price, new_revenue = expected_revenue(original_price, selected_discount / 100, original_demand, ped)
        
        display_product_details(tab2, selected_product, selected_category, ped, original_price,
                                original_demand, original_price * original_demand, new_price, new_demand, new_revenue)
    else:
        tab2.write("No products found.")
