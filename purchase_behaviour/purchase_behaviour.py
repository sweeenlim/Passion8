import os
import psycopg2
from dotenv import load_dotenv
import sqlalchemy
import pandas as pd
import numpy as np
import datetime as dt
from lifetimes import BetaGeoFitter, GammaGammaFitter
import matplotlib.pyplot as plt
from lifetimes.plotting import plot_period_transactions
import seaborn as sns
import streamlit as st

# load from .env file
current_dir = os.getcwd()
# parent_dir = os.path.dirname(current_dir)
parent_dir = current_dir
load_dotenv(f'{parent_dir}/.env')

print(f"Current Directory: {current_dir}")
print(f"Parent Directory: {parent_dir}")

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
        return df
    except Exception as e:
        print("An error occurred:", e)
        connection.rollback() 
    finally:
        connection.close()  

def create_full_table():
    full_table = create_df('online_sales')
    tables = {'products': 'product_id',
              'users': 'user_id',
              'ratings': 'product_id'
              }
    for key, value in tables.items():
        df = create_df(key)
        full_table = pd.merge(full_table, df, on=value, how='inner')

    full_table['total_price'] = np.where(
    full_table['Coupon_Status'] == 'Used',
    full_table['Quantity'] * full_table['actual_price'] * (1 - full_table['Discount_pct']),
    full_table['Quantity'] * full_table['actual_price']
    )

    return full_table

def bg_nbd():
    today_date = dt.datetime(2020, 1, 1)
    sales = create_full_table()

    cltv_prediction = sales.groupby('user_id').agg({
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

bgf, df = bg_nbd()

# plot top n customers in num_weeks
# n, num_weeks is dynamic
def top_customers(n, num_weeks, df):
    top_customers_num_weeks = bgf.conditional_expected_number_of_purchases_up_to_time(num_weeks,  # number of weeks
                                                            df["frequency"],
                                                            df["recency"],
                                                            df["T"]).sort_values(ascending=False).head(n)
    return top_customers_num_weeks

def plot_top_customers(n, num_weeks, df):
    top_customers_num_weeks = top_customers(int(n), int(num_weeks), df)

    fig = plt.figure(figsize=(10, 6))
    top_customers_num_weeks.plot(kind='bar', color='skyblue')
    plt.title(f'Top {n} Customers - Expected Purchases in the {num_weeks} Week')
    plt.xlabel('Customer')
    plt.ylabel('Expected Number of Purchases')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

# plot_top_customers(10, 1, df)
    
# number of transactions expected by the company in num_weeks
# num_weeks is dynamic
def expected_num_transactions(num_weeks, df):
    res = []
    weeks = []
    for week in range(num_weeks):
        num_transactions_in_week = bgf.predict(week+1, df["frequency"], df["recency"], df["T"]).sum()
        res.append(num_transactions_in_week)
        weeks.append(week)
    return weeks, res

def plot_expected_num_transactions(num_weeks, df):
    weeks, expected_transactions = expected_num_transactions(num_weeks, df)
    fig = plt.figure(figsize=(10, 6))
    plt.plot(weeks, expected_transactions, marker='o', color='b', linestyle='-')
    plt.title('Expected Number of Transactions Over the Next 4 Weeks')
    plt.xlabel('Week')
    plt.ylabel('Expected Number of Transactions')
    plt.xticks(weeks)
    plt.grid(True)
    plt.tight_layout()
    return fig

# plot_expected_num_transactions(4, df)
    
# gamma-gamma model
def gamma_gamma(df):
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(df["frequency"], df["monetary"])
    return ggf

ggf = gamma_gamma(df)

def cltv(df):
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

    df_final = df.merge(cltv, on="user_id", how="left")
    # cltv_final["segment"]=pd.qcut(cltv_final["clv"],4,labels=["Low","Medium","High","Top"])
    return df_final

# segmentize and plot cltv
def bin_cltv(df, labels, bins):
    # Segment based on custom bins
    df = cltv(df)
    df['clv_segment'] = pd.cut(df['clv'], bins=bins, labels=labels)
    return df

def plot_cltv(df, labels, bins):
    df = bin_cltv(df, labels, bins)
    segment_counts = df['clv_segment'].value_counts().reindex(labels)

    plt.figure(figsize=(10, 6))
    segment_counts.plot(kind='bar', color=['lightcoral', 'skyblue', 'lightgreen', 'gold'])
    plt.title("Customer Segments Based on Custom CLTV Bins")
    plt.xlabel("CLV Segment")
    plt.ylabel("Number of Customers")
    plt.xticks(rotation=0)
    plt.show()

bins = [0, 100, 1000, 10000, float('inf')] # this should be dynamic
labels = ["Low", "Medium", "High", "Top"]

# plot_cltv(df, labels, bins)

st.title("Customer Segmentation")

st.header("")
top_num_customers = st.number_input("Number of customers?", step = 1)
top_num_weeks = st.number_input("Number of weeks sir?", step = 1)

if top_num_customers and top_num_weeks:
    st.pyplot(plot_top_customers(top_num_customers, top_num_weeks, df))

expected_num_weeks = st.number_input("Number of weeks", step = 1)

if expected_num_weeks:
    st.pyplot(plot_expected_num_transactions(expected_num_weeks, df))