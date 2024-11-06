import streamlit as st
from tabs.tab2a import load_data_jj, display_tab2a, display_tab2b, display_tab2c

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Subgroup A", page_icon="📝")
    st.markdown("# Subgroup A")

    tab1, tab2, tab3 = st.tabs(["🔍Customer Analysis", "📉 Customer Churn Rates","📬Marketing Channel Analysis"])
    
    df_jj = load_data_jj()
    # Display content for tab2
    display_tab2a(tab2, df_jj)
    display_tab2b(tab2, df_jj)
    display_tab2c(tab2, df_jj)
if __name__ == "__main__":
    main()