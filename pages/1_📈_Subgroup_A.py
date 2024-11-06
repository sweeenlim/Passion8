import streamlit as st
from tabs.tab1a import display_tab1a

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Subgroup A", page_icon="📝")
    st.markdown("# Subgroup A")

    tab1, tab2, tab3 = st.tabs(["🔍Customer Analysis", "📉 Customer Churn Rates","📬Marketing Channel Analysis"])
    
    display_tab1a(tab1)

if __name__ == "__main__":
    main()