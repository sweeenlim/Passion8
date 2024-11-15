import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
import os
import psycopg2
import numpy as np

# Load environment variables
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
load_dotenv(f"{parent_dir}/.env")

postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_port_no = os.getenv("POSTGRES_PORT")
host = os.getenv("POSTGRES_HOST")
database = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")


def get_db_connection():
    """Get a database connection."""
    return psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=postgres_password,
        port=postgres_port_no,
    )


def load_data_jj():
    """Load and preprocess online_sales data."""
    with get_db_connection() as conn:
        print("Connected to database")
        # Get products table
        products_df = pd.read_sql_query("SELECT * FROM products", conn)
        products_df.drop(
            ["about_product", "discounted_price", "discount_percentage"],
            axis=1,
            inplace=True,
        )

        # Get online_sales data
        sales_df = pd.read_sql_query("SELECT * FROM online_sales", conn)
        sales_df.drop(["delivery_charges"], axis=1, inplace=True)

    df_2019 = pd.merge(sales_df, products_df, on="product_id", how="left")
    # Reorder columns
    df_2019 = df_2019[
        [
            "cust_id",
            "transaction_id",
            "date",
            "product_id",
            "product_name",
            "category",
            "coupon_code",
            "coupon_status",
            "discount_percentage",
            "quantity",
            "actual_price",
        ]
    ]
    df_2019 = df_2019.rename(columns={"cust_id": "user_id"})
    # Add a Quarter column
    df_2019["date"] = pd.to_datetime(df_2019["date"])
    position = df_2019.columns.get_loc("date") + 1
    df_2019.insert(loc=position, column="quarter", value=df_2019["date"].dt.quarter)
    # Generating synthetic data for 2018

    # Set seed for reproducibility
    np.random.seed(3101)

    # Number of synthetic transactions for 2018
    n_transactions = len(df_2019)

    # Generate synthetic transaction IDs (unique)
    transaction_ids = np.arange(1, n_transactions + 1)

    # Generate random dates in 2018
    start_date = pd.to_datetime("2018-01-01")
    end_date = pd.to_datetime("2018-12-31")
    transaction_dates = start_date + (end_date - start_date) * np.random.rand(
        n_transactions
    )

    # Generate synthetic product_ids sampled from the 2019 data
    product_ids = np.random.choice(df_2019["product_id"].unique(), size=n_transactions)

    # Generate synthetic quantities
    quantities = np.random.randint(
        1, np.percentile(df_2019["quantity"], 90) + 1, size=n_transactions
    )

    # Create the synthetic 2018 dataset
    df_2018 = pd.DataFrame(
        {
            "transaction_id": transaction_ids,
            "date": transaction_dates,
            "product_id": product_ids,
            "quantity": quantities,
        }
    )

    # Left join with the products table
    df_2018 = pd.merge(df_2018, products_df, on="product_id", how="left")
    # Reorder columns
    df_2018 = df_2018[
        [
            "transaction_id",
            "date",
            "product_id",
            "product_name",
            "category",
            "quantity",
            "actual_price",
        ]
    ]

    # Add quarter column
    df_2018.insert(
        loc=df_2018.columns.get_loc("date") + 1,
        column="quarter",
        value=df_2018["date"].dt.quarter,
    )

    # Add empty columns to simulate no coupon strategy is used

    df_2018.insert(
        loc=df_2018.columns.get_loc("category") + 1, column="coupon_code", value=np.nan
    )
    df_2018.insert(
        loc=df_2018.columns.get_loc("coupon_code") + 1,
        column="coupon_status",
        value=np.nan,
    )
    df_2018.insert(
        loc=df_2018.columns.get_loc("coupon_status") + 1,
        column="discount_percentage",
        value=0,
    )

    # Generate synthetic user_ids based on 2019 data

    # Create a dictionary with unique user_ids for each quarter in 2019

    unique_users_per_quarter_2019 = (
        df_2019.groupby("quarter")["user_id"].unique().to_dict()
    )

    # Create a function to assign similar user ids which appears in each quarter in 2019 to each quarter in 2018.
    def assign_user_ids(row):
        quarter = row["quarter"]
        unique_users = unique_users_per_quarter_2019.get(quarter, [])
        return np.random.choice(unique_users, size=1)[0]

    # Assign user ids
    df_2018.insert(
        loc=0, column="user_id", value=df_2018.apply(assign_user_ids, axis=1)
    )

    # Randomly remove 20% of rows to simulate poorer performance due to no retention strategy

    df_2018 = df_2018.sample(frac=0.8, random_state=42)
    df_2018 = df_2018.reset_index(drop=True)
    # Combine 2018 and 2019 dataframe into a single dataframe
    df = pd.concat([df_2018, df_2019], ignore_index=True)
    # Create a total_spent column to indicate how much a customer spends each transaction
    df["total_spent"] = df.apply(
        lambda row: (
            row["actual_price"] * row["quantity"] * (1 - row["discount_percentage"])
            if row["coupon_status"] == "Used"
            else row["actual_price"] * row["quantity"]
        ),
        axis=1,
    )
    # Create a column to show year and quarter
    df["year_quarter"] = df["date"].dt.to_period("Q")
    return df


# Define a function to calculate churn rate


def calculate_churn_rate(df):
    # Group unique users into the respective year and quarter
    customers_per_quarter = df.groupby("year_quarter")["user_id"].unique().reset_index()
    churn_rates = []

    for i in range(1, len(customers_per_quarter)):
        current_customers = set(customers_per_quarter["user_id"].iloc[i])
        previous_customers = set(customers_per_quarter["user_id"].iloc[i - 1])

        # Taking a set difference to identify customers present in the previous quarter but not in the current quarter
        churned_customers = previous_customers - current_customers

        # Churn rate: percentage of previous customers who churned
        churn_rate = len(churned_customers) / len(previous_customers)

        churn_rates.append(
            {
                "year_quarter": customers_per_quarter["year_quarter"].iloc[i],
                "churn_rate": churn_rate,
            }
        )
    churn_rate_df = pd.DataFrame(churn_rates)
    churn_rate_df["year_quarter"] = churn_rate_df["year_quarter"].astype(str)
    return churn_rate_df


def display_tab2a(tab2, df):
    churn_rate_df = calculate_churn_rate(df)
    # Create and display line chart
    fig = px.line(
        churn_rate_df,
        x="year_quarter",
        y="churn_rate",
        markers=True,
        title="Churn Rate By Quarter",
    )
    # Customize the line style and hover information
    fig.update_traces(
        line=dict(width=2, color="royalblue"),
        marker=dict(size=8),
        hovertemplate="Year-Quarter: %{x}<br>Churn Rate: %{y:.1%}",  # Custom hover template
        hoverlabel=dict(
            bgcolor="#1fe0fb",  # Background color of the hover box
            font_size=14,  # Font size of the hover text
            font_color="black",  # Text color within the hover box
        ),
    )

    # Customize the layout
    fig.update_layout(
        xaxis_title="Year and Quarter",  # Custom x-axis label
        yaxis_title="Churn Rate (%)",  # Custom y-axis label
        yaxis_tickformat=".1%",  # Format y-axis as percentage
        hovermode="x unified",  # Unified hover mode
    )
    tab2.plotly_chart(fig)
    tab2.write(
        "Churn rate is defined quarterly. For example, a user that makes a transaction in the previous quarter but not in the next quarter will be marked as churned."
    )


def display_tab2b(tab2, df):
    df["coupon_status"] = df["coupon_status"].fillna("Not Used")
    # Count coupons used or not used by year and quarter
    coupon_counts = (
        df.groupby(["year_quarter", "coupon_status"]).size().reset_index(name="count")
    )
    coupon_counts["year_quarter"] = coupon_counts["year_quarter"].astype(str)

    # Calculate the total transactions per year_quarter
    total_transactions = (
        coupon_counts.groupby("year_quarter")["count"].sum().reset_index()
    )
    total_transactions.columns = ["year_quarter", "total_count"]

    # Plot the stacked bar chart with Plotly Express
    fig = px.bar(
        coupon_counts,
        x="year_quarter",
        y="count",
        color="coupon_status",
        title="Coupon Usage",
        labels={"year_quarter": "Year_Quarter", "count": "Number of Transactions"},
        color_discrete_map={
            "Used": "lightgreen",
            "Not Used": "lightcoral",
        },  # Specify colors
    )

    # Customize hover box to show more details
    fig.update_traces(
        hovertemplate="Year Quarter: %{x}<br>Transactions: %{y}<extra></extra>",
    )

    # Update hover label settings (font size and background color)
    fig.update_layout(
        hoverlabel=dict(
            font_size=14,  # Increase font size
            font_color="black",  # Set font color to black
            bordercolor="black",  # Border color of the hover box,
        ),
        legend=dict(traceorder="reversed"),  # Reverse the order of the legend items
    )

    # Update layout for axis labels and x-axis rotation
    fig.update_layout(
        xaxis_title="Year and Quarter",
        yaxis_title="Number of Transactions (Thousand)",
        xaxis=dict(tickangle=0),  # Set rotation to 0
        legend_title_text="Coupon Status",
    )

    # Add annotations for total transactions at the top of each bar
    for i, row in total_transactions.iterrows():
        fig.add_annotation(
            x=row["year_quarter"],
            y=row["total_count"],
            text=f"{row['total_count']}",
            showarrow=False,
            yshift=10,  # Shift annotation slightly above the bar
            font=dict(color="black", size=12),
        )
    tab2.plotly_chart(fig)


def display_tab2c(tab2, df):

    # Filter data for 2018 and 2019
    revenue_2018 = (
        df[df["date"].dt.year == 2018]
        .groupby("quarter")["total_spent"]
        .sum()
        .reset_index()
    )
    revenue_2019 = (
        df[df["date"].dt.year == 2019]
        .groupby("quarter")["total_spent"]
        .sum()
        .reset_index()
    )

    # Convert total_spent to millions
    revenue_2018["total_spent"] = revenue_2018["total_spent"] / 1e6
    revenue_2019["total_spent"] = revenue_2019["total_spent"] / 1e6

    # Create the figure
    fig = go.Figure()

    # Add 2018 revenue line
    fig.add_trace(
        go.Scatter(
            x=revenue_2018["quarter"].astype(str),
            y=revenue_2018["total_spent"],
            mode="lines+markers",
            name="2018",
            line=dict(color="blue"),
            marker=dict(symbol="circle"),
            hovertemplate="Quarter %{x}<br>Total Revenue: $%{y:.1f}M",
        )
    )

    # Add 2019 revenue line
    fig.add_trace(
        go.Scatter(
            x=revenue_2019["quarter"].astype(str),
            y=revenue_2019["total_spent"],
            mode="lines+markers",
            name="2019",
            line=dict(color="green"),
            marker=dict(symbol="circle"),
            hovertemplate="Quarter %{x}<br>Total Revenue: $%{y:.1f}M",
        )
    )

    # Update layout with titles and labels
    fig.update_layout(
        title="Total Revenue per Quarter in 2018 and 2019",
        xaxis_title="Quarter",
        yaxis_title="Total Revenue (Millions)",
        yaxis_tickformat="$,.1fM",
        xaxis=dict(tickangle=0),
        legend_title_text="Year",
        hovermode="x unified",
        legend=dict(traceorder="reversed"),  # Reverse the order of the legend items
    )

    # Set x-axis as categorical
    fig.update_xaxes(type="category")

    # Update y-axis to show specified ticks
    fig.update_yaxes(
        range=[2, 10],  # Set the range to 0 to 10
        tickvals=[2, 4, 6, 8, 10],  # Set custom tick values
    )

    # Display the plot in Streamlit
    tab2.plotly_chart(fig)
