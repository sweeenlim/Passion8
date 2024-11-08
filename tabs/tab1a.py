import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import datetime as dt
from lifetimes import BetaGeoFitter, GammaGammaFitter
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import sqlalchemy

# load from .env file
current_dir = os.getcwd()
# parent_dir = os.path.dirname(current_dir)
parent_dir = current_dir
load_dotenv(f'{parent_dir}/.env')

postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_port_no = os.getenv('POSTGRES_PORT_NO')
host = os.getenv('POSTGRES_HOST')
database = os.getenv('POSTGRES_DB')
user = os.getenv('POSTGRES_USER')

engine = sqlalchemy.create_engine(f'postgresql://{user}:{postgres_password}@{host}:{postgres_port_no}/{database}')

# function to create df
def create_df(table_name):
    try:
        connection = engine.connect() 
        query = f'''
        SELECT 
            *
        FROM
            {table_name} 
        '''
        
        df = pd.read_sql(query, con=connection)
        if table_name=="users":
            df = df.rename(columns={"user_id": "cust_id"})
        return df
    except Exception as e:
        print("An error occurred:", e)
        connection.rollback() 
    finally:
        connection.close() 

def create_full_table():
    full_table = create_df('online_sales')
    tables = {'products': 'product_id',
              'users': 'cust_id',
              'ratings': 'product_id'
              }
    for key, value in tables.items():
        df = create_df(key)
        full_table = pd.merge(full_table, df, on=value, how='inner')
    
    full_table['total_price'] = np.where(
    full_table['coupon_status'] == 'Used',
    full_table['quantity'] * full_table['actual_price'] * (1 - full_table['discount_percentage_x']),
    full_table['quantity'] * full_table['actual_price']
    )
    full_table['date'] = pd.to_datetime(full_table['date'], errors='coerce')
    return full_table

def plot_historical_rfm():
    df = create_full_table()
    df['total_price'] = df['total_price'].astype(float)

    # Set a dummy reference date for recency calculations
    reference_date = pd.to_datetime('2020-01-01')
    rfm = df.groupby('cust_id').agg({
        'date': lambda x: (reference_date - x.max()).days,  
        'transaction_id': 'count',                         
        'total_price': 'sum'                             
    })

    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    # Rank each customer for Recency, Frequency, and Monetary
    rfm['Recency_rank'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm['Frequency_rank'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['Monetary_rank'] = pd.qcut(rfm['Monetary'].astype(float), 5, labels=[1, 2, 3, 4, 5])  # Ensuring Monetary is float

    rfm['RFM_Score'] = rfm['Recency_rank'].astype(int) + rfm['Frequency_rank'].astype(int) + rfm['Monetary_rank'].astype(int)

    # Customer segmentation based on RFM score
    rfm['Segment'] = pd.cut(rfm['RFM_Score'], bins=[2, 5, 8, 11, 15], labels=['Low', 'Medium', 'High', 'Top'])
    labels=['Low', 'Medium', 'High', 'Top']
    rfm_segment_counts = rfm['Segment'].value_counts().reindex(labels)
    
    # Convert the series to a DataFrame for Plotly
    rfm_segment_counts_df = rfm_segment_counts.reset_index()
    rfm_segment_counts_df.columns = ['RFM Segment', 'Number of Customers']

    # Create a bar plot using Plotly Express
    fig = px.bar(
        rfm_segment_counts_df,
        x='RFM Segment',
        y='Number of Customers',
        title="RFM Customer Segments Barplot",
        labels={'Number of Customers': 'Number of Customers'},
        color='RFM Segment',
        color_discrete_map={
            "Low": "lightcoral",
            "Medium": "skyblue",
            "High": "lightgreen",
            "Top": "gold"
        }
    )
    
    # Customize layout
    fig.update_layout(
        xaxis_title="RFM Segment",
        yaxis_title="Number of Customers",
        xaxis=dict(categoryorder='array', categoryarray=labels),
        template="plotly_white"
    )
    
    return fig

def plot_historical_cltv():
    df = create_full_table()
    # Aggregate data at the customer level
    cltv = df.groupby('cust_id').agg({
        'transaction_id': 'nunique',           # Number of orders (Frequency)
        'total_price': 'sum',                  # Total revenue (Monetary)           
        'product_id': 'nunique',               # Number of unique products purchased
        'date': 'max'
    }).reset_index()
    cltv.columns = ['cust_id', 'total_orders', 'total_revenue', 'unique_products', 'last_purchase_date']

    cltv['AOV'] = cltv['total_revenue'] / cltv['total_orders']
    cltv['purchase_frequency'] = cltv['total_orders']/(cltv.shape[0])
    cltv['customer_value'] = cltv['purchase_frequency'] * cltv['AOV']
    repeat_rate = cltv[cltv["total_orders"] > 1].shape[0] / cltv.shape[0]
    churn_rate = 1 - repeat_rate    
    cltv["profit_margin"] = cltv["total_revenue"] * 0.20
    cltv["cltv"] = cltv["customer_value"] / churn_rate * cltv["profit_margin"]

    # Define the fixed CLTV thresholds
    bins = [0, 10000, 100000, 1000000, float('inf')]  
    labels = ["Low", "Medium", "High", "Top"]
    cltv["bin_segment"] = pd.cut(cltv["cltv"], bins=bins, labels=labels, right=False)
    cltv = cltv.sort_values(by="bin_segment", ascending=False)
    cltv_binned = cltv["bin_segment"].value_counts().reindex(labels)

    # Convert the series to a DataFrame for Plotly
    cltv_binned_df = cltv_binned.reset_index()
    cltv_binned_df.columns = ['CLTV Segment', 'Number of Customers']

    # Create a bar plot using Plotly Express
    fig = px.bar(
        cltv_binned_df,
        x='CLTV Segment',
        y='Number of Customers',
        title="Customer Segment Distribution",
        labels={'Number of Customers': 'Number of Customers'},
        color='CLTV Segment',
        color_discrete_map={
            "Low": "lightcoral",
            "Medium": "skyblue",
            "High": "lightgreen",
            "Top": "gold"
        }
    )
    
    # Customize layout
    fig.update_layout(
        xaxis_title="CLTV Segment",
        yaxis_title="Number of Customers",
        xaxis=dict(categoryorder='array', categoryarray=labels),
        template="plotly_white"
    )
    
    return fig



def bg_nbd():
    today_date = dt.datetime(2020, 1, 1)
    sales = create_full_table()

    cltv_prediction = sales.groupby('cust_id').agg({
        'date': [min, max],
        'transaction_id': 'nunique', 
        'total_price': 'sum',
    })

    cltv_prediction.columns = ['earliest_date', 'latest_date', 'frequency', 'monetary']

    cltv_prediction['recency'] = (cltv_prediction['latest_date'] - cltv_prediction['earliest_date']).dt.days
    cltv_prediction["monetary"] = cltv_prediction["monetary"] / cltv_prediction["frequency"]
    cltv_prediction['T'] = (today_date - cltv_prediction['earliest_date']).dt.days

    # he BG/NBD model assumes that customers have already made some repeat purchases to establish a purchasing pattern. 
    # When frequency is 0, there isn’t enough data for the model to make reliable predictions about future transactions hence, remove frequency = 0
    cltv_prediction = cltv_prediction[(cltv_prediction["frequency"] > 1)]
    # some users have multiple transactions on only one day
    cltv_prediction = cltv_prediction[(cltv_prediction["recency"] > 0)]

    cltv_prediction["T"] = cltv_prediction["T"] / 7
    cltv_prediction["recency"] = cltv_prediction["recency"] / 7

    cltv_prediction = cltv_prediction.drop(columns=['earliest_date', 'latest_date'])

    bgf = BetaGeoFitter(penalizer_coef=0.001)
    bgf.fit(cltv_prediction["frequency"], cltv_prediction["recency"], cltv_prediction["T"])

    return bgf, cltv_prediction



# plot top n customers in num_weeks
# n, num_weeks is dynamic
def top_customers(n, num_weeks, df, bgf):
    top_customers_num_weeks = bgf.conditional_expected_number_of_purchases_up_to_time(num_weeks,  # number of weeks
                                                            df["frequency"],
                                                            df["recency"],
                                                            df["T"]).sort_values(ascending=False).head(n)
    return top_customers_num_weeks


def plot_top_customers(n, num_weeks, df, bgf):
    top_customers_num_weeks = top_customers(int(n), int(num_weeks), df, bgf)
    
    top_customers_num_weeks = top_customers_num_weeks.reset_index()
    top_customers_num_weeks.columns = ['cust_id', 'expected_purchases'] 
    
    fig = px.bar(
        top_customers_num_weeks,
        x='cust_id',
        y='expected_purchases',
        title=f'Top {n} Customers Expected Purchases in {num_weeks} Week(s)',
        labels={'cust_id': 'Customer', 'expected_purchases': 'Expected Number of Purchases'},
        color='expected_purchases',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        xaxis=dict(title='User ID', type='category'),
        yaxis=dict(title='Expected Number of Purchases'),
        coloraxis_showscale=False 
    )
    
    return fig
    
# number of transactions expected by the company in num_weeks
# num_weeks is dynamic
def expected_num_transactions(num_weeks, df, bgf):
    res = []
    weeks = []
    for week in range(num_weeks):
        num_transactions_in_week = bgf.predict(week+1, df["frequency"], df["recency"], df["T"]).sum()
        res.append(num_transactions_in_week)
        weeks.append(week)
    return weeks, res
    
def plot_expected_num_transactions(num_weeks, df, bgf):
    weeks, expected_transactions = expected_num_transactions(num_weeks, df, bgf)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=weeks,
        y=expected_transactions,
        mode='lines+markers',
        marker=dict(color='red'),
        line=dict(color='red'),
        name='Expected Transactions'
    ))

    fig.update_layout(
        title=f'Expected Number of Transactions Over the Next {num_weeks} Weeks',
        xaxis_title='Week',
        yaxis_title='Expected Number of Transactions',
        xaxis=dict(tickmode='linear', tickvals=weeks),  # Ensure all weeks are shown on x-axis
        template='plotly_white'
    )
    
    return fig

# gamma-gamma model
def gamma_gamma(df):
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(df["frequency"], df["monetary"])
    return ggf


def cltv(df, bgf, ggf):
    df["expected_average_profit"] = ggf.conditional_expected_average_profit(df["frequency"], df["monetary"])

    cltv = ggf.customer_lifetime_value(bgf,
                                    df["frequency"],
                                    df["recency"],
                                    df["T"],
                                    df["monetary"],
                                    time=3, # 3 months, how many months account do you want?
                                    freq="W", # frequency information of T
                                    discount_rate=0.01)
    cltv = cltv.reset_index()

    df_final = df.merge(cltv, on="cust_id", how="left")
    return df_final

# segmentize and plot cltv
def bin_cltv(df, labels, bins):
    # Segment based on custom bins
    df = cltv(df)
    df['clv_segment'] = pd.cut(df['clv'], bins=bins, labels=labels)
    return df

def plot_vip(df, n, bgf, ggf):
    df = cltv(df, bgf, ggf)

    top_vip_customers = df[['cust_id', 'clv']].sort_values(by='clv', ascending=False).head(n)
    
    fig = px.bar(
        top_vip_customers,
        x='cust_id',
        y='clv',
        title=f'Top {n} VIP Customers by Predicted CLTV',
        labels={'cust_id': 'User ID', 'clv': 'Predicted CLTV'},
        color='clv',
        color_continuous_scale='Viridis'
    ).update_yaxes(categoryorder="total descending")
    
    # Customize layout
    fig.update_layout(
        xaxis=dict(title='User ID', type='category'),
        yaxis=dict(title='Predicted CLTV'),
        coloraxis_showscale=False
    )
    
    return fig

# streamlit outline
def display_tab1a(tab1):
    '''Display content for tab1a'''

    bgf, df = bg_nbd()
    ggf = gamma_gamma(df)

    tab1.title("Customer Segmentation and VIP Prediction")
    tab1.write("Analyze historical sales data, predict customer segments, and estimate customer lifetime value (CLTV) with the BG/NBD and Gamma-Gamma models.")

    # RFM Analysis Plot
    tab1.header("Historical RFM (Recency, Frequency, Monetary) Analysis")
    tab1.write("Recency: Number of days since the customer's last purchase.")
    tab1.write("Frequency: Total number of purchases made by the customer within the time frame. In this case, it is the throughout the year of 2019.")
    tab1.write("Monetary: Sum of all the purchases made by the customer in the time frame.")
    tab1.write("Each customer was assigned a score from 1 to 5 for Recency, Frequency, and Monetary. Summing these would form the overall RFM score.")
    tab1.write("Segments: Low (2-5), Medium (6-8), High (9-11), Top (12-15)")  

    tab1.plotly_chart(plot_historical_rfm())  

    # CLTV Prediction Plot
    tab1.header("Historical Customer Lifetime Value (CLTV)")
    tab1.write("CLTV = ((Average Order Value x Purchase Frequency) / Churn Rate) x Profit margin")
    tab1.write("Components: ")
    tab1.write("Average Order Value: Total revenue divided by the number of orders.")
    tab1.write("Purchase Frequency: Total orders divided by total customers.")
    tab1.write("Churn Rate: Ratio of customers with no repeat orders.")
    tab1.write("Profit Margin: Set to 20%, based on Amazon seller average margins.")
 
    tab1.plotly_chart(plot_historical_cltv())

    # Top N Customers' Expected Purchases in X Weeks
    tab1.header("Predicted Highest Purchasing Customers in Future Weeks")
    tab1.write("The BG/NBD model is a probabilistic model used to predict a customer’s future purchase behavior based on their past transactional data.")
    top_num_customers = tab1.number_input("Enter the number of customers:", step=1, min_value=1, value=10)
    top_num_weeks = tab1.number_input("Enter the number of weeks:", step=1, min_value=1)

    if top_num_customers > 0 and top_num_weeks > 0:
        tab1.plotly_chart(plot_top_customers(top_num_customers, top_num_weeks, df, bgf))

    # Expected Number of Total Purchases in X Weeks
    tab1.header("Predicted Number of Purchases in Future Weeks")
    expected_num_weeks = tab1.number_input("Enter the number of weeks:", step=1, min_value=1, value=4)

    if expected_num_weeks > 0:
        tab1.plotly_chart(plot_expected_num_transactions(expected_num_weeks, df, bgf))

    # Top n VIPs Prediction
    tab1.header("VIP Customers Prediction")
    tab1.write("The Gamma-Gamma submodel is used to predict the monetary value of customer transactions, given that the customer is active.")
    tab1.write("Customer Lifetime Value (CLTV): By multiplying the frequency of future transactions (from the BG/NBD model) with the expected transaction value (from the Gamma-Gamma model), we can predict each customer’s lifetime value.")
    n_vip = tab1.number_input("Enter the number of customers:", step=1, value=10)

    if n_vip > 0:
        tab1.plotly_chart(plot_vip(df, n_vip, bgf, ggf))
