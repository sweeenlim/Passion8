import streamlit as st
from tabs.bonus_computer_vision import display_computer_vision_tab
from tabs.bonus_ai_chatbot import display_ai_chatbot_tab

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Bonus", page_icon="⭐",layout="wide")
    st.markdown("# Bonus")

    tab1, tab2, tab3 = st.tabs(["💬 AI Recommendation Chatbot","🖼️ Computer Vision", "🔤 Sentiment Analysis"])
    
    # Display the AI Chatbot tab
    display_ai_chatbot_tab(tab1)

    # Load data
    # Display content for tab1
    display_computer_vision_tab(tab2)
    
if __name__ == "__main__":
    main()