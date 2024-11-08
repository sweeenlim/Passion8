import streamlit as st
from tabs.tab1a import display_tab1a
from tabs.tab2a import load_data_jj, display_tab2a, display_tab2b, display_tab2c
from tabs.tab3a import load_data_wy, display_tab3a, display_tab3b, display_tab3c, display_tab3d, display_tab3e

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Subgroup A", page_icon="📝")
    st.markdown("# Subgroup A")

    tab1, tab2, tab3 = st.tabs(["🔍Customer Analysis", "📉 Customer Churn Rates","📬Marketing Channel Analysis"])
    
    # Display content for tab1
    display_tab1a(tab1)

    # Display content for tab2
    df_jj = load_data_jj()
    display_tab2a(tab2, df_jj)
    display_tab2b(tab2, df_jj)
    display_tab2c(tab2, df_jj)

    # Display content for tab3
    sales_data = load_data_wy()
    display_tab3a(tab3, sales_data)
    display_tab3b(tab3, sales_data)
    display_tab3c(tab3, sales_data)
    display_tab3d(tab3, sales_data)
    display_tab3e(tab3, sales_data)

if __name__ == "__main__":
    main()