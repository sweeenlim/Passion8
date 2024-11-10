import pandas as pd
import os
import nltk
import numpy as np
from h2ogpte import H2OGPTE
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from IPython.display import Markdown
import streamlit as st


load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

#### Load environment variables ####
h2o_api_key = os.getenv('H2O_API_KEY_EMAIL')
postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_port_no = os.getenv('POSTGRES_PORT')
host = os.getenv('POSTGRES_HOST')
database = os.getenv('POSTGRES_DB')
user = os.getenv('POSTGRES_USER')

# Download NLTK resources
nltk.download('stopwords')

#### Connect to PostgreSQL database and load relevant table ####
engine = create_engine(f'postgresql://{user}:{postgres_password}@{host}:{postgres_port_no}/{database}')
online_sales = pd.read_sql("SELECT * FROM online_sales", engine)
products = pd.read_sql("SELECT * FROM products", engine)
users = pd.read_sql("SELECT * FROM users", engine)
products.drop(['discounted_price', 'discount_percentage'], axis=1, inplace=True)
df = pd.merge(online_sales, products, on='product_id', how='left')


##### Product Recommendations #####
def user_based_recommendation(cust_id, df, top_n=3):
    """
    Recommend top N products for a given user based on user similarity.

    Parameters:
    - cust_id (int): The ID of the user for whom to generate recommendations.
    - df (DataFrame): The preprocessed DataFrame containing user transactions.
    - top_n (int): Number of top recommendations to return.

    Returns:
    - recommendations (list): List of recommended product IDs.
    """

    # Check if the cust_id exists in the DataFrame
    if cust_id not in df['cust_id'].unique():
        print(f"User ID {cust_id} not found in the dataset.")
        return []

    # 1. Create the User-Item Matrix
    user_item_matrix = df.pivot_table(index='cust_id',
                                      columns='product_id',
                                      values='quantity',
                                      aggfunc='sum',
                                      fill_value=0)

    # 2. Compute User Similarity Matrix using Cosine Similarity
    # Cosine similarity returns values between 0 and 1
    similarity_matrix = cosine_similarity(user_item_matrix)
    
    # Convert the similarity matrix to a DataFrame for easier handling
    similarity_df = pd.DataFrame(similarity_matrix, 
                                 index=user_item_matrix.index, 
                                 columns=user_item_matrix.index)

    # 3. Find Similar Users
    # Get similarity scores for the target user
    user_similarities = similarity_df[cust_id].sort_values(ascending=False)
    
    # Exclude the target user from the similarity scores
    user_similarities = user_similarities.drop(labels=[cust_id])

    # Select top similar users (you can adjust the number, e.g., top 10)
    top_similar_users = user_similarities.head(10).index.tolist()

    if not top_similar_users:
        print(f"No similar users found for User ID {cust_id}.")
        return []

    # 4. Aggregate Products from Similar Users
    # Select the purchase data of similar users
    similar_users_data = df[df['cust_id'].isin(top_similar_users)]

    # Aggregate the quantities for each product from similar users
    product_scores = similar_users_data.groupby('product_id')['quantity'].sum()

    # 5. Exclude Products Already Purchased by the Target User
    # Get the list of products already purchased by the target user
    user_purchased_products = df[df['cust_id'] == cust_id]['product_id'].unique()

    # Remove these products from the recommendation candidates
    product_scores = product_scores.drop(labels=user_purchased_products, errors='ignore')

    if product_scores.empty:
        print(f"No new products to recommend for User ID {cust_id}.")
        return []

    # 6. Sort the products based on the aggregated scores in descending order
    sorted_products = product_scores.sort_values(ascending=False)

    # 7. Select the Top N Products
    recommended_products = sorted_products.head(top_n).index.tolist()

    # Print the recommended products with their names
    recommended_product_names = products[products['product_id'].isin(recommended_products)]['product_name'].tolist()

    return recommended_products, recommended_product_names

# Define a function to preprocess text
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    
    # Tokenize, remove stop words, and apply stemming
    tokens = text.split()
    tokens = [stemmer.stem(word) for word in tokens if word.lower() not in stop_words]
    
    return ' '.join(tokens)

def content_based_recommendation(cust_id, transactions_df, products_df, top_n=5):
    """
    Recommend top N products for a given user based on content similarity.
    
    Parameters:
    - cust_id (int): The ID of the user for whom to generate recommendations.
    - transactions_df (DataFrame): The DataFrame containing user transactions.
    - products_df (DataFrame): The DataFrame containing product details.
    - top_n (int): Number of top recommendations to return.
    
    Returns:
    - recommendations (list): List of recommended product IDs.
    """
    
    # Check if the cust_id exists in the transactions DataFrame
    if cust_id not in transactions_df['cust_id'].unique():
        print(f"User ID {cust_id} not found in the dataset.")
        return []

    # 1. Create a new feature by combining relevant product attributes in the products DataFrame
    products_df['combined_features'] = products_df['product_name'] + ' ' + products_df['about_product'] + ' ' + products_df['category']
    
    # 2. Apply text preprocessing to the combined features
    products_df['combined_features'] = products_df['combined_features'].apply(preprocess_text)
    
    # 3. Remove duplicate products to ensure each product is unique
    products_df = products_df[['product_id', 'combined_features','actual_price']].drop_duplicates().reset_index(drop=True)
    
    # 4. Initialize the TF-IDF Vectorizer
    tfidf = TfidfVectorizer(stop_words='english')
    
    # 5. Fit and transform the combined features
    tfidf_matrix = tfidf.fit_transform(products_df['combined_features'])
    
    # 6. Compute the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    
    # 7. Create a reverse mapping of product indices and IDs
    indices = pd.Series(products_df.index, index=products_df['product_id']).drop_duplicates()
    
    # 8. Get the list of products purchased by the user from the transactions DataFrame
    user_purchases = transactions_df[transactions_df['cust_id'] == cust_id]['product_id'].unique()
    
    # 9. Initialize a series to hold similarity scores
    similarity_scores = pd.Series(dtype=float)
    
    # 10. Iterate over each purchased product and accumulate similarity scores
    for product_id in user_purchases:
        if product_id not in indices:
            continue  # Skip if the product_id is not in the dataset
        idx = indices[product_id]
        sim_scores = pd.Series(cosine_sim[idx]).sort_values(ascending=False)
        sim_scores = sim_scores.iloc[1:]  # Exclude the product itself
        similarity_scores = similarity_scores.add(sim_scores, fill_value=0)
    
    if similarity_scores.empty:
        print(f"No similar products found for User ID {cust_id}.")
        return []
    
    # 11. Remove products already purchased by the user
    similarity_scores = similarity_scores.drop(labels=[indices[pid] for pid in user_purchases if pid in indices], errors='ignore')
    
    if similarity_scores.empty:
        print(f"No new products to recommend for User ID {cust_id}.")
        return []
    
    # 12. Sort the products based on similarity scores and price (for upselling)
    similarity_scores = similarity_scores.sort_values(ascending=False)
    top_indices = similarity_scores.head(top_n * 2).index.tolist()  # Get more candidates
    
    # 13. Map indices back to product IDs and filter by price
    recommended_products = products_df.iloc[top_indices]
    recommended_products = recommended_products.sort_values(by='actual_price', ascending=False)  # Prioritize higher-priced items
    recommended_product_ids = recommended_products.head(top_n)['product_id'].tolist()
    
    return recommended_product_ids

def popularity_based_recommendation(transactions_df, products_df, top_n=5, category=None):
    """
    Recommend top N popular products based on overall sales or within a specific category.
    
    Parameters:
    - transactions_df (DataFrame): DataFrame containing user transactions with columns ['cust_id', 'product_id', 'quantity', ...].
    - products_df (DataFrame): DataFrame containing product details with columns ['product_id', 'product_name', 'about_product', 'category', ...].
    - top_n (int): Number of top recommendations to return.
    - category (str, optional): If specified, recommend popular products within this category.
    
    Returns:
    - recommended_product_ids (list): List of recommended product IDs.
    """
    
    # Merge transactions with products to get category information
    merged_df = transactions_df.merge(products_df, on='product_id', how='left')
    
    # If category is specified, filter by category
    if category:
        merged_df = merged_df[merged_df['category'] == category]
    
    # Aggregate the total quantity sold for each product
    product_sales = merged_df.groupby('product_id')['quantity'].sum().sort_values(ascending=False)
    
    # Get the top N product IDs
    recommended_product_ids = product_sales.head(top_n).index.tolist()
    
    return recommended_product_ids

def cold_start_recommendation(cust_id, transactions_df, products_df, users_df=None, top_n=5):
    """
    Recommend top N products for a new user using a hybrid approach combining popularity and demographic-based recommendations.
    
    Parameters:
    - cust_id (int): The ID of the user for whom to generate recommendations.
    - transactions_df (DataFrame): DataFrame containing user transactions with columns ['cust_id', 'product_id', 'quantity', ...].
    - products_df (DataFrame): DataFrame containing product details with columns ['product_id', 'product_name', 'about_product', 'category', ...].
    - users_df (DataFrame, optional): DataFrame containing user demographic details with columns ['cust_id', 'age', 'gender', 'location', ...].
    - top_n (int): Number of top recommendations to return.
    
    Returns:
    - recommended_product_ids (list): List of recommended product IDs.
    """
    
    # Check if the user exists in the transactions (i.e., is not a new user)
    if cust_id in transactions_df['cust_id'].unique():
        print(f"User ID {cust_id} exists in the dataset. Use user-based or content-based recommendations instead.")
        return []
    
    # Initialize a dictionary to hold recommendation scores
    rec_scores = {}
    
    popular_recs = popularity_based_recommendation(transactions_df, products_df, top_n=top_n*2)
    for pid in popular_recs:
        rec_scores[pid] = rec_scores.get(pid, 0) + 1  # Weight can be adjusted as needed

    # Sort the products based on accumulated scores in descending order
    sorted_recs = sorted(rec_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Extract product IDs from the sorted list
    recommended_product_ids = [pid for pid, score in sorted_recs]
    
    # Remove duplicates while preserving order
    recommended_product_ids = list(dict.fromkeys(recommended_product_ids))
    
    # Limit to top_n recommendations
    recommended_product_ids = recommended_product_ids[:top_n]
    
    # If not enough recommendations, fallback to popularity-based
    if len(recommended_product_ids) < top_n:
        additional_recs = popularity_based_recommendation(transactions_df, products_df, top_n=top_n - len(recommended_product_ids))
        # Append additional recommendations, ensuring no duplicates
        for pid in additional_recs:
            if pid not in recommended_product_ids:
                recommended_product_ids.append(pid)
            if len(recommended_product_ids) == top_n:
                break
    
    return recommended_product_ids

def overall_recommendation(cust_id, transactions_df, products_df, top_n=5):
    """
    Generate a consolidated list of product recommendations for a user by integrating
    User-Based Collaborative Filtering, Content-Based Filtering, and Cold Start strategies.
    
    Parameters:
    - cust_id (int): The ID of the user for whom to generate recommendations.
    - transactions_df (DataFrame): DataFrame containing user transactions with columns ['cust_id', 'product_id', 'Quantity', ...].
    - products_df (DataFrame): DataFrame containing product details with columns ['product_id', 'product_name', 'about_product', 'category', ...].
    - users_df (DataFrame, optional): DataFrame containing user demographic details with columns ['cust_id', 'age', 'gender', 'location', ...].
    - top_n (int): Number of top recommendations to return.
    
    Returns:
    - final_recommendations (list): List of recommended product IDs.
    - final_recommendation_names (list, optional): List of recommended product names (if available in products_df).
    """
    
    # Initialize a dictionary to hold aggregated recommendation scores
    recommendation_scores = {}
    
    # Check if the user exists in the transactions (i.e., is not a new user)
    if cust_id in transactions_df['cust_id'].unique():
        print(f"Existing User: Generating recommendations using User-Based and Content-Based strategies.\n")
        
        # 1. User-Based Collaborative Filtering Recommendations
        print("Generating User-Based Collaborative Filtering Recommendations...")
        user_based_recs, user_based_names = user_based_recommendation(cust_id, transactions_df, top_n=top_n)
        for pid in user_based_recs:
            recommendation_scores[pid] = recommendation_scores.get(pid, 0) + 2  # Assign higher weight
        
        print("Generating Content-Based Recommendations...")
        # 2. Content-Based Recommendations
        content_based_recs = content_based_recommendation(cust_id, transactions_df, products_df, top_n=top_n)
        for pid in content_based_recs:
            recommendation_scores[pid] = recommendation_scores.get(pid, 0) + 1  # Assign lower weight
        
    else:
        print(f"New User: Generating recommendations using Cold Start strategy.")
        
        # 3. Cold Start Recommendations
        cold_start_recs = cold_start_recommendation(cust_id, transactions_df, products_df, top_n=top_n)
        for pid in cold_start_recs:
            recommendation_scores[pid] = recommendation_scores.get(pid, 0) + 1  # Assign weight
        
    # Convert the recommendation_scores dictionary to a DataFrame for sorting
    rec_scores_df = pd.DataFrame(list(recommendation_scores.items()), columns=['product_id', 'score'])
    
    # Sort the recommendations based on the aggregated scores in descending order
    rec_scores_df = rec_scores_df.sort_values(by='score', ascending=False)
    
    # Extract the top_n product_ids
    top_recommendations = rec_scores_df.head(top_n)['product_id'].tolist()
    
    print("Generating Final Recommendations...  Done!")
    # Optionally, retrieve product names for better readability
    if 'product_name' in products_df.columns:
        # Ensure that all product_ids are present in products_df
        valid_pids = [pid for pid in top_recommendations if pid in products_df['product_id'].values]
        product_names = products_df.set_index('product_id').loc[valid_pids]['product_name'].tolist()
        return top_recommendations, product_names
    else:
        return top_recommendations
    
#### Connect to H2O.ai's GPTE API ####
h2o_endpoint = 'https://h2ogpte.genai.h2o.ai'
client = H2OGPTE( # Initialize the H2OGPTE client
    address=h2o_endpoint,
    api_key=h2o_api_key
)

#### Generate personalized email content using H2O.ai's GPTE ####

# Summarizing product descriptions
def summarize_description(description):
    """
    Summarize a product description using H2OGPTE to make it more concise.

    Parameters:
    - description (str): The long product description to summarize.

    Returns:
    - summary (str): A concise version of the product description.
    """
    # Create a prompt to summarize the description
    summary_prompt = f"Summarize the following product description concisely:\n\n{description}"

    # Start a chat session for summarization
    chat_session_id = client.create_chat_session()
    with client.connect(chat_session_id) as session:
        reply = session.query(summary_prompt, timeout=60)
    
    # Return the summarized description
    summary = reply.content.strip()
    return summary

def generate_personalized_email_h2o(user_id):
    """
    Generate personalized email content with summarized product descriptions, image links, and discount coupons.

    Parameters:
    - user_id (int): ID of the user for whom to generate the email.

    Returns:
    - email_content (str): Generated personalized email content.
    """

    # Retrieve user demographics
    user_info = users[users['user_id'] == user_id].iloc[0].to_dict()

    # Generate product recommendations
    recommendations, _ = overall_recommendation(user_id, df, products, top_n=5)

    # Format email details
    formatted_recs = []
    for pid in recommendations:
        product_name = products.loc[products['product_id'] == pid, 'product_name'].values[0]
        about_product = products.loc[products['product_id'] == pid, 'about_product'].values[0]
        category = products.loc[products['product_id'] == pid, 'category'].values[0]
        actual_price = products.loc[products['product_id'] == pid, 'actual_price'].values[0]
        img_link = products.loc[products['product_id'] == pid, 'img_link'].values[0]
        discount_coupon = online_sales[online_sales['product_id'] == pid]['coupon_code'].values[0] if not online_sales[online_sales['product_id'] == pid]['coupon_code'].isnull().all() else "No discount available"
        discount_pct = online_sales[online_sales['product_id'] == pid]['discount_percentage'].values[0] if not online_sales[online_sales['product_id'] == pid]['discount_percentage'].isnull().all() else 0

        # Summarize the product description
        summarized_description = summarize_description(about_product)
        
        # Add the summarized product details to the list
        formatted_recs.append({
            'product_name': product_name,
            'about_product': summarized_description,
            'category': category,
            'actual_price': actual_price,
            'img_link': img_link,
            'discount_coupon': discount_coupon,
            'discount_pct': discount_pct,
        })

    # Create the prompt for H2O.ai LLM
    prompt = f"""
    Create a personalized email from Amazon for User ID {user_id}.
    
    User Information:
    Age: {user_info.get('age')}
    Gender: {user_info.get('gender')}
    
    Recommended Products:
    """
    for rec in formatted_recs:
        prompt += f"""
        - Product: {rec['product_name']}
        Category: {rec['category']}
        Description: {rec['about_product']}
        Price: ${rec['actual_price']}
        Image Link: {rec['img_link']}
        Discount: {rec['discount_coupon']} - {rec['discount_pct'] * 100}% off
        """

    prompt += f"""
    Email Content:
    Dear Customer {user_id},

    As a valued member of the Amazon family, we’re always looking for ways to make your shopping experience even better. Based on your recent interests, we’ve curated some product recommendations that we think you’ll love.

    Here’s what we’ve picked out for you:

    [Include the list of recommended products with descriptions, images, and exclusive discount codes, if available.]
    """

    # Start a chat session
    chat_session_id = client.create_chat_session()

    # Send the prompt to the model within the chat session
    with client.connect(chat_session_id) as session:
        reply = session.query(prompt, timeout=60)

    # Extract the generated email content
    main_content = reply.content.strip()

    # Append the closing text
    closing_text = "\n\nThank you for choosing Amazon. We look forward to helping you find more products you love.\n\nWarm regards,\n\nYour Amazon Team"
    email_content = main_content + closing_text
    return email_content

#### Streamlit App ####
def display_personalized_email_tab(tab):
    """Display content for personalized email tab."""
    tab.title("Personalized Email Generation")
    tab.write("Generate personalized email content for users based on their preferences.")
    
    # Display user selection dropdown
    user_id = tab.selectbox("Select User ID:", online_sales['cust_id'].unique().tolist())
    
    # Generate personalized email content
    if tab.button("Generate Email"):
        with st.spinner('Generating email...'):
            email_content = generate_personalized_email_h2o(user_id)
        tab.write(f"**Email Content for User ID {user_id}:**")
        tab.write(email_content, unsafe_allow_html=True)