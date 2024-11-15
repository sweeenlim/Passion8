import streamlit as st
from tabs.bonus_computer_vision import display_computer_vision_tab
from tabs.bonus_ai_chatbot import display_ai_chatbot_tab
from tabs.bonus_sentiment_analysis import display_sentiment_analysis_tab
from tabs.bonus_personalized_email import display_personalized_email_tab


def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="Bonus",
        page_icon="⭐",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.page_link("Hello.py", label="⬅ BACK")
    st.markdown("# Bonus")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "💬 AI Recommendation Chatbot",
            "🖼️ Computer Vision",
            "🔤 Sentiment Analysis",
            "📧 AI Personalized Marketing",
        ]
    )

    # Display the AI Chatbot tab
    display_ai_chatbot_tab(tab1)

    # Load data
    # Display content for tab1
    display_computer_vision_tab(tab2)

    display_sentiment_analysis_tab(tab3)

    display_personalized_email_tab(tab4)


if __name__ == "__main__":
    main()
