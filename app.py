from fastapi import FastAPI, UploadFile
from tabs.bonus_computer_vision import predict_product_category, load_product_categorisation_model, search_similar_products
from tabs.bonus_sentiment_analysis import get_vader_score, load_vader
from tabs.bonus_personalized_email import generate_personalized_email_h2o
from tabs.bonus_ai_chatbot import get_recommendation

app = FastAPI(title="Passion8", description="Ecommerce Analysis and Optimization", version="0.1.0")

@app.post("/bonus/analyse_sentiment", tags=["Bonus"])
async def analyse_sentiment(review:str):
    model = load_vader()
    score = get_vader_score(review, model)
    if score >= 0.5:
        return "Positive"
    elif score <= -0.5:
        return "Negative"
    else:
        return "Neutral"


@app.post("/bonus/classify_product", tags=["Bonus"])
async def classify_product_image(file: UploadFile):

    model = load_product_categorisation_model()
    product_category = predict_product_category(model, file.file.read())

    return product_category

@app.post("/bonus/search_similar_products", tags=["Bonus"])
async def search_similar_products(file: UploadFile,number_of_products:int):
    similar_products = search_similar_products(file.file.read(),number_of_products)
    similar_products_link = [i[0] for i in similar_products]
    return similar_products_link

@app.post("/bonus/generate_personalized_email", tags=["Bonus"])
async def generate_personalized_email(user_id: int):
    return generate_personalized_email_h2o(user_id)


@app.post("/bonus/get_product_recommendation", tags=["Bonus"])
async def get_product_recommendation(user_query:str):
    chat_session_id = None
    return get_recommendation(chat_session_id,user_query)