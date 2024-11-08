import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
import streamlit as st
from h2ogpte import H2OGPTE

# Explicitly specify the path to the .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

h2o_api = os.getenv('H2O_API_KEY')
h20_collection_id = os.getenv('H2O_PRODUCTS_COLLECTION_ID')


# Initialize the H2OGPTE client
client = H2OGPTE(
    address='https://h2ogpte.genai.h2o.ai',
    api_key= h2o_api,
)

collection_id = h20_collection_id


def display_ai_chatbot_tab(tab):
    """Displays the AI Chatbot content within the specified Streamlit tab."""
    with tab:
        st.title("RAGccoBot🤖")

        # Initialize chat session
        chat_session_id = client.create_chat_session(collection_id)

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        if user_input := st.chat_input("What are you looking for today?"):
            # Display the user's message in the chat container
            with st.chat_message("user"):
                st.markdown(user_input)
            # Add user's message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Query the LLM with the user's input
            with client.connect(chat_session_id) as session:
                reply = session.query(
                    message=user_input,  # Use the actual user input here
                    llm='gpt-4o',
                    rag_config={
                        "rag_type": "rag",
                    },
                    system_prompt=f"""
You are a friendly and helpful customer service agent at an online store, assisting customers with personalized product recommendations from our collection. Your goal is to carefully understand the customer’s query and suggest the most relevant product to meet their needs.

If the customer’s query is vague or lacks specific details, politely ask clarifying questions to better understand their preferences. Pay close attention to any hints in the query that could help you identify suitable products, such as desired features, uses, or types.

### Important Product Information
- **product_name**: Contains the name of each product in the collection.
- **product_id**: A unique identifier for each product.
- **about_product**: A brief description of each product.


### Response Instructions
- Provide a friendly, brief explanation of why the recommended product is a good fit for the customer.
- Include the product’s name (from **product_name**), followed by the product ID (from **product_id**) in parentheses.
- Please include the image link of the product to display it in the chat if you can find it online on amazon website.

### Response Format
Your response should follow this structure for each recommendation:

- **Product Name** (Product ID: `product_id`)

If you cannot find a suitable product, politely ask the customer for more details to help refine your recommendation. Remember to source the whole collection for the best match.

User Query: "{user_input}"
"""
                )
                bot_response = reply.content

            # Display the chatbot's response
            with st.chat_message("assistant"):
                st.markdown(bot_response)
            # Add chatbot's response to chat history
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
