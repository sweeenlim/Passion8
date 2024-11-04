import streamlit as st
from tabs.tab1b import load_data, display_tab1

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Subgroup B", page_icon="📈")
    st.markdown("# Subgroup B")

    tab1, tab2, tab3 = st.tabs(["📈 Demand Forecast", "💰 Pricing Strategies","🚚 Supply Chain Efficiency"])
    
    # Load data
    actual_data, forecast_data, products = load_data()

    # Display content for tab1
    display_tab1(tab1, actual_data, forecast_data, products)
    
if __name__ == "__main__":
    main()