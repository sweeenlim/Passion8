import pandas as pd
import datetime as dt
from lifetimes import BetaGeoFitter, GammaGammaFitter

def create_cltv_prediction_table(sales, today_date):
    # Aggregate sales data by user
    cltv_prediction = sales.groupby('user_id').agg({
        'date': [min, max],
        'transaction_id': 'nunique',
        'total_price': 'sum',
    })
    cltv_prediction.columns = ['earliest_date', 'latest_date', 'frequency', 'monetary']
    
    # Calculate recency and tenure (T)
    cltv_prediction['recency'] = (cltv_prediction['latest_date'] - cltv_prediction['earliest_date']).dt.days
    cltv_prediction["monetary"] = cltv_prediction["monetary"] / cltv_prediction["frequency"]
    cltv_prediction['T'] = (today_date - cltv_prediction['earliest_date']).dt.days
    
    # Filter for users with more than one purchase and positive recency
    cltv_prediction = cltv_prediction[(cltv_prediction["frequency"] > 1)]
    cltv_prediction = cltv_prediction[(cltv_prediction["recency"] > 0)]
    
    # Convert recency and T to weeks
    cltv_prediction["T"] = cltv_prediction["T"] / 7
    cltv_prediction["recency"] = cltv_prediction["recency"] / 7
    
    return cltv_prediction.drop(columns=['earliest_date', 'latest_date'])

def fit_bgf_model(cltv_prediction, penalizer_coef=0.01):
    # Initialize and fit BetaGeoFitter model
    bgf = BetaGeoFitter(penalizer_coef=penalizer_coef)
    bgf.fit(cltv_prediction["frequency"], cltv_prediction["recency"], cltv_prediction["T"])
    return bgf

def get_top_customers(bgf, cltv_prediction, weeks=1, top_n=10):
    # Predict top customers likely to purchase in the next specified weeks
    top_customers = bgf.conditional_expected_number_of_purchases_up_to_time(
        weeks, cltv_prediction["frequency"], cltv_prediction["recency"], cltv_prediction["T"]
    ).sort_values(ascending=False).head(top_n)
    return top_customers

def predict_monthly_transactions(bgf, cltv_prediction, weeks=4):
    # Predict the total number of transactions in the next month
    return bgf.predict(weeks, cltv_prediction["frequency"], cltv_prediction["recency"], cltv_prediction["T"]).sum()

def fit_ggf_model(cltv_prediction, penalizer_coef=0.01):
    # Initialize and fit GammaGammaFitter model
    ggf = GammaGammaFitter(penalizer_coef=penalizer_coef)
    ggf.fit(cltv_prediction["frequency"], cltv_prediction["monetary"])
    return ggf

def calculate_cltv(bgf, ggf, cltv_prediction, time=3, freq="W", discount_rate=0.01):
    # Calculate customer lifetime value (CLTV)
    cltv = ggf.customer_lifetime_value(
        bgf, cltv_prediction["frequency"], cltv_prediction["recency"], cltv_prediction["T"],
        cltv_prediction["monetary"], time=time, freq=freq, discount_rate=discount_rate
    )
    cltv = cltv.reset_index()
    cltv_final = cltv_prediction.merge(cltv, on="user_id", how="left")
    return cltv_final

def segment_cltv(cltv_final, bins=[0, 500, 1000, 10000, float('inf')], labels=["Low", "Medium", "High", "Top"]):
    # Segment customers based on CLTV values
    cltv_final['clv_segment'] = pd.cut(cltv_final['clv'], bins=bins, labels=labels)
    return cltv_final

def main(sales_data, today_date):
    # Run the CLTV analysis workflow
    cltv_prediction = create_cltv_prediction_table(sales_data, today_date)
    bgf = fit_bgf_model(cltv_prediction)
    top_customers = get_top_customers(bgf, cltv_prediction)
    monthly_transactions = predict_monthly_transactions(bgf, cltv_prediction)
    
    ggf = fit_ggf_model(cltv_prediction)
    cltv_final = calculate_cltv(bgf, ggf, cltv_prediction)
    cltv_final = segment_cltv(cltv_final)
    
    # Display results
    print(f"Top 10 customers and their probability of making a purchase in the following week:\n{top_customers}")
    print(f"Expected number of transactions in the next month: {monthly_transactions}")
    print(cltv_final[['user_id', 'clv', 'clv_segment']].head(10))
    return cltv_final

# Example usage
# sales_data = create_full_table()  # Replace with actual data loading
# today_date = dt.datetime(2020, 1, 1)
# cltv_results = main(sales_data, today_date)
