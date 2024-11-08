import base64
import streamlit as st
import streamlit.components.v1 as com


# Embed the animation
st.markdown('<div class="center-lottie">', unsafe_allow_html=True)
com.iframe("https://lottie.host/embed/57930a62-cb53-47b8-b028-a287a7715222/RskPzQ3i5e.json", width=300)
st.markdown('</div>', unsafe_allow_html=True)

# Set the page background
st.markdown(
    f"""
    <style>
    [data-testid="stMain"] {{
        background: url(data:image/png;base64,{base64.b64encode(open("/Users/marcus/Desktop/nus/Y4S1/DSA3101/Passion8/pages/assets/passion8.png", "rb").read()).decode()});
        background-size: cover;          /* Ensures the image covers the container */
        background-repeat: no-repeat;    /* Prevents the image from tiling */
        background-position: bottom;     /* Centers the image in the container */
    }}


    [data-testid="stHeader"]{{
        opacity: 0.5;
    }}

    """,
    unsafe_allow_html=True,
)

st.markdown("<br><br><br><br><br><br><br><br>", unsafe_allow_html=True)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.page_link('pages/1_📈_Subgroup_A.py', label=':blue[**Customer Analysis**]', use_container_width=False)

with col2:
    st.page_link('pages/1_📈_Subgroup_A.py', label=':blue[**Customer Churn Rates**]', use_container_width=False)

with col3:
    st.page_link('pages/1_📈_Subgroup_A.py', label=':blue[**Marketing Channels**]', use_container_width=False)

with col4:
    st.page_link('pages/2_📊_Subgroup_B.py', label=':blue[**Demand Forecast**]', use_container_width=False)


col5, col6, col7, col8,= st.columns(4)

with col5:
    st.page_link('pages/2_📊_Subgroup_B.py', label=':blue[**Pricing Strategies**]', use_container_width=False)

with col6:
    st.page_link('pages/2_📊_Subgroup_B.py', label=':blue[**Supply Chain Efficiency**]', use_container_width=False)

with col7:
    st.page_link('pages/3_⭐_Bonus.py', label=':blue[**Supply Chain Efficiency**]', use_container_width=False)

with col8:
    st.page_link('pages/3_⭐_Bonus.py', label=':blue[**Sentiment Analysis**]', use_container_width=False)


col9, col10, col11, = st.columns(3)

with col9:
    st.page_link('pages/3_⭐_Bonus.py', label=':blue[**AI Reccomendation Bot**]', use_container_width=False)

with col10:
    st.page_link('pages/3_⭐_Bonus.py', label=':blue[**Computer Vision**]', use_container_width=False)

# with col11:
#     st.page_link('pages/3_⭐_Bonus.py', label=':blue[**Computer Vision**]', use_container_width=False)
