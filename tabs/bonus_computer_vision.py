import io
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import psycopg2
from io import StringIO
from PIL import Image
from tensorflow.keras.models import Model, model_from_json, load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from sklearn.neighbors import NearestNeighbors

postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_port_no = os.getenv('POSTGRES_PORT_NO')
host = os.getenv('POSTGRES_HOST')
database = os.getenv('POSTGRES_DB')
user = os.getenv('POSTGRES_USER')


def get_db_connection():
    """Get a database connection."""
    return psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=postgres_password,
        port=postgres_port_no,
    )

def load_df():
    with get_db_connection() as conn:
        print("Connected to database")
        # Get products table 
        df = pd.read_sql_query("SELECT * FROM products", conn)

    return df


def load_product_categorisation_model():
    json_file = open('../Passion8/computer_vision/model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("../Passion8/computer_vision/model.weights.h5")
    print("Loaded model from disk")

    loaded_model.compile(loss='sparse_categorical_crossentropy',
                optimizer=Adam(),
                metrics=['accuracy'])
    
    return loaded_model

def predict_product_category(loaded_model, img_bytes):   
    image = Image.open(io.BytesIO(img_bytes)).convert('RGB').resize((150, 150))
    image = np.array(image) / 255.0  # Convert to numpy array and normalize
    image = np.expand_dims(image, axis=0)

    class_names = ['In-Ear',
                   'SmartTelevisions',
                   'Smartphones',
                   'Irons,Steamers&Accessories',
                   'Cables']

    predictions = loaded_model.predict(image)
    pred_labels = np.argmax(predictions, axis=1)
    cat = class_names[pred_labels[0]]
    return cat

def search_similar_products(img_bytes, k=5):
    df = pd.read_csv("computer_vision/amazon_embeddings.csv")
    # df = load_df()
    # load KNN model
    knn_model = pickle.load(open('computer_vision/knn_pickle_file', 'rb'))

    # load embedding model
    base_model = VGG16(weights='imagenet', include_top=False)
    embedding_model = Model(inputs=base_model.input, outputs=base_model.output)

    # load input image and generate embedding  

    input_img = Image.open(io.BytesIO(img_bytes)).convert('RGB').resize((224, 224))
    img_array = np.array(input_img)[np.newaxis, ...]  # Add batch dimension
    img_array = preprocess_input(img_array)
    input_embedding = embedding_model.predict(img_array)
    input_embedding = input_embedding.flatten()
    # input_embedding.flatten()
    distances, indices = knn_model.kneighbors([input_embedding])    
    # distances, indices = knn_model.predict([input_embedding])    
    similar_images = [(df.iloc[idx]['img_link'], dist) for idx, dist in zip(indices[0], distances[0])]

    return similar_images


def display_computer_vision_tab(tab):
    """Display content for cv tab."""

    tab.title("Classify Product Category")
    tab.write("Upload an image to predict the product category.")
    tab.write("""
    **Supported categories**:
    - In-Ear
    - SmartTelevisions
    - Smartphones
    - Irons,Steamers&Accessories
    - Cables
    """)
    
    uploaded_file = tab.file_uploader("Choose a file",key = 1)
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        tab.image(bytes_data, width=300)
        
        # Load model and predict product category
        model = load_product_categorisation_model()
        product_category = predict_product_category(model, bytes_data)
        tab.write(f"Predicted product category: <span style='color: green;'>**{product_category}**</span>", unsafe_allow_html=True)


    tab.title("Search for Similar Products")
    uploaded_file = tab.file_uploader("Choose a file", key=2)
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        tab.image(bytes_data, width=300)
        similar_images = search_similar_products(bytes_data, k=5)
        tab.write("Similar images:")
        for img_link, dist in similar_images:
            tab.image(img_link, width=300)



    


