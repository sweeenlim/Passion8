import base64
import os
import streamlit as st
import streamlit.components.v1 as com

st.set_page_config(
    page_title="Passion8",
    page_icon="8️⃣",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": "For detailed implementations, please visit https://github.com/freedytan/Passion8."
    },
)


# Load the background css
current_dir = os.path.dirname(os.path.abspath(__file__))
bg = os.path.join(current_dir, "pages/assets", "bg.css")

with open(bg) as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    @import url('https://fonts.cdnfonts.com/css/magz');
    @import url('https://fonts.googleapis.com/css2?family=Kanit:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

    .title {
        font-family: 'Magz', sans-serif;
        color: #196ddd;
        font-size: 6.4vw;
        font-weight: normal;
        height: 100px;
    }
    .big-text {
        font-family: 'Kanit', sans-serif;
        font-size: 2vw; 
        color: white;
        background-color: #196ddd;
        padding: 1vw;
        border-radius: 0.5vw;
        text-align: left;
        font-style: normal;
        display: inline-block;
    }
    .spacer {
        margin-top: 2vw; 
    }
    .col4, .col5, .col6 {
        font-family: 'Kanit', sans-serif;
        background-color: #f0f0f0;
        padding: 2vw;
        border-radius: 1vw;
        font-style: italic;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Create columns for title and logo
title, logo = st.columns([3, 1])

with title:
    st.markdown('<h2 class="title">Passion8</h2>', unsafe_allow_html=True)
with logo:
    com.iframe(
        "https://lottie.host/embed/57930a62-cb53-47b8-b028-a287a7715222/RskPzQ3i5e.json"
    )

# Display the text
st.markdown(
    '<div class="big-text">Ecommerce Analysis and Optimization</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

# Create columns for links
col1, col2, col3 = st.columns(3)

with col1:
    st.page_link(
        "pages/1_📈_Subgroup_A.py",
        label=":blue-background[**Subgroup A**]",
        use_container_width=False,
    )

with col2:
    st.page_link(
        "pages/2_📊_Subgroup_B.py",
        label=":blue-background[**Subgroup B**]",
        use_container_width=False,
    )

with col3:
    st.page_link(
        "pages/3_⭐_Bonus.py",
        label=":blue-background[**Bonus**]",
        use_container_width=False,
    )

# Create three columns for words
col4, col5, col6 = st.columns(3)

# Define lists of words for each column
words_col4 = ["Customer Analysis", "Customer Churn Rates", "Marketing Channel Analysis"]
words_col5 = ["Demand Forecast", "Pricing Strategies", "Supply Chain Efficiency"]
words_col6 = [
    "AI Recommendation Bot",
    "Computer Vision",
    "Sentiment Analysis",
    "Personalized Email",
]


# Generate HTML strings for each column
html_col4 = (
    "<div class='col4'>"
    + "".join(
        [f"<span style='color:#00008B'>- {word}</span><br>" for word in words_col4]
    )
    + "</div>"
)
html_col5 = (
    "<div class='col5'>"
    + "".join(
        [f"<span style='color:#00008B'>- {word}</span><br>" for word in words_col5]
    )
    + "</div>"
)
html_col6 = (
    "<div class='col6'>"
    + "".join(
        [f"<span style='color:#00008B'>- {word}</span><br>" for word in words_col6]
    )
    + "</div>"
)
# Render the HTML strings in the columns
with col4:
    st.markdown(html_col4, unsafe_allow_html=True)

with col5:
    st.markdown(html_col5, unsafe_allow_html=True)

with col6:
    st.markdown(html_col6, unsafe_allow_html=True)
# Close the centered container
st.markdown("</div>", unsafe_allow_html=True)
