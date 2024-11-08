import base64
import os
import streamlit as st
import streamlit.components.v1 as com

st.set_page_config(page_title="Passion8", page_icon="8️⃣", initial_sidebar_state="collapsed")

# Encode the background image
current_dir = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(current_dir, 'pages/assets', 'passion8.png')
background_image = base64.b64encode(open(img_path, "rb").read()).decode()

# Add CSS with fixed background
st.markdown(
    f"""
    <style>
    /* Main container settings */
    [data-testid="stAppViewContainer"] {{
        height: 100vh;
        overflow: hidden;
        
    }}
    
    /* Background image settings */
    [data-testid="stMain"] {{
        background: url(data:image/png;base64,{background_image});
        background-size: cover;
        background-repeat: no-repeat;
        background-position: bottom;
        overflow: hidden;
    }}

    /* Header transparency */
    [data-testid="stHeader"] {{
        opacity: 0.5;
    }}
    
    /* Content layout */
    .main {{
        padding-top: 0 !important;
    }}
    
    /* Center content */
    .center-content {{
        display: flex;
        flex-direction: column;
        align-items: center;
    }}

    /* Lottie animation container */
    .center-lottie {{
        display: flex;
        justify-content: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Wrap content in a centered container
st.markdown('<div class="center-content">', unsafe_allow_html=True)

# Embed the animation
st.markdown('<div class="center-lottie">', unsafe_allow_html=True)
com.iframe("https://lottie.host/embed/57930a62-cb53-47b8-b028-a287a7715222/RskPzQ3i5e.json",height=160, width=300)
st.markdown('</div>', unsafe_allow_html=True)

# Add some spacing
st.markdown("<br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)

# Create columns for links
col1, col2, col3 = st.columns(3)

with col1:
    st.page_link('pages/1_📈_Subgroup_A.py', label=':blue-background[**Subgroup A**]', use_container_width=False)

with col2:
    st.page_link('pages/2_📊_Subgroup_B.py', label=':blue-background[**Subgroup B**]', use_container_width=False)

with col3:
    st.page_link('pages/3_⭐_Bonus.py', label=':blue-background[**Bonus**]', use_container_width=False)

# Create three columns for words
col4, col5, col6 = st.columns(3)
        
# Define lists of words for each column
words_col4 = ["Customer Analysis", "Customer Churn Rates", "Marketing Channel Analysis"]
words_col5 = ["Demand Forecast", "Pricing Strategies", "Supply Chain Efficiency"]
words_col6 = ["AI Recommendation Bot", "Computer Vision", "Semtiment Analysis"]

with col4:
    for word in words_col4:
        st.markdown(f"<span style='color:#00008B'>- {word}</span>", unsafe_allow_html=True)

with col5:
    for word in words_col5:
        st.markdown(f"<span style='color:#00008B'>- {word}</span>", unsafe_allow_html=True)

with col6:
    for word in words_col6:
        st.markdown(f"<span style='color:#00008B'>- {word}</span>", unsafe_allow_html=True)

# Close the centered container
st.markdown('</div>', unsafe_allow_html=True)