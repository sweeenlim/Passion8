import streamlit as st
from tabs.bonus_computer_vision import display_computer_vision_tab

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Bonus", page_icon="⭐")
    st.markdown("# Bonus")

    tab1, tab2 = st.tabs(["🖼️ Computer Vision", "🔤 Sentiment Analysis"])
    
    # Load data
    # Display content for tab1
    display_computer_vision_tab(tab1)
    
if __name__ == "__main__":
    main()