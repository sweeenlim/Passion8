import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
import os
import psycopg2
import networkx as nx
from mlxtend.frequent_patterns import apriori, association_rules
import plotly.graph_objects as go

# Load environment variables
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
load_dotenv(f'{parent_dir}/.env')

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

def load_data_wy():
    """Load data"""
    sales_data = pd.read_csv('marketing_channels/marketing_channels.csv')
    return sales_data

def display_tab3a(tab3, sales_data):
    with tab3:
        # Section Title
        st.subheader("ROI Analysis by Marketing Channel")

        # Dropdown selection for ROI type
        roi_type = st.selectbox(
            "Select ROI Type",
            options=["Average Non-Adjusted ROI", "Average Adjusted ROI"]
        )

        # Determine the ROI column based on selection
        if roi_type == "Average Non-Adjusted ROI":
            roi_column = "ROI"
        else:
            roi_column = "ROI_adjusted" 

        # Unique marketing channels for the filter
        marketing_channels = sales_data['marketing_channel'].unique()
        selected_channels = st.multiselect(
            "Select Marketing Channels to Display",
            options=marketing_channels,
            default=marketing_channels, 
            key="channel_selector_tab3a"  # Unique key to avoid duplicate ID error
        )

        filtered_data = sales_data[sales_data['marketing_channel'].isin(selected_channels)]
        avg_roi_by_channel = (
            filtered_data.groupby("marketing_channel")[roi_column]
            .mean()
            .reset_index()
            .sort_values(by=roi_column, ascending=False)  # Sort in descending order
        )

        fig = px.bar(
            avg_roi_by_channel,
            x="marketing_channel",
            y=roi_column,
            title=f"{roi_type} by Marketing Channel",
            labels={roi_column: roi_type, "marketing_channel": "Marketing Channel"},
            hover_data=["marketing_channel", roi_column],
            color=roi_column,  
            color_continuous_scale="Blues" 
        )

        fig.update_layout(
            xaxis=dict(title="Marketing Channel", tickangle=-45),
            yaxis=dict(title="Average ROI"),
            margin=dict(l=40, r=40, t=40, b=80)
        )
    tab3.plotly_chart(fig)

def display_tab3b(tab3, sales_data):
    with tab3:
        # Section Title
        st.subheader("Seasonal ROI Trend Over Time by Marketing Channel")

        # Ensure the 'date' column is in datetime format
        sales_data['date'] = pd.to_datetime(sales_data['date'], errors='coerce')

        # Convert min_date and max_date to datetime format for st.slider compatibility
        min_date = sales_data['date'].min().to_pydatetime()
        max_date = sales_data['date'].max().to_pydatetime()
        date_range = st.slider(
            "Select Date Range",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date)
        )

        # Filter data based on the selected date range
        filtered_data = sales_data[(sales_data['date'] >= date_range[0]) & 
                                   (sales_data['date'] <= date_range[1])]

        # Multiselect for marketing channels with a unique key
        marketing_channels = filtered_data['marketing_channel'].unique()
        selected_channels = st.multiselect(
            "Select Marketing Channels to Display",
            options=marketing_channels,
            default=marketing_channels,
            key="seasonality_channel_selector_tab3b"
        )

        # Further filter data based on selected channels
        filtered_data = filtered_data[filtered_data['marketing_channel'].isin(selected_channels)]

        # Group by month and marketing channel, calculating the mean seasonal ROI
        filtered_data['year_month'] = filtered_data['date'].dt.to_period('M')
        seasonality_data = filtered_data.groupby(['year_month', 'marketing_channel'])['ROI_seasonal_adjusted'].mean().reset_index()

        # Explicitly convert 'year_month' back to a standard datetime format
        seasonality_data['year_month'] = seasonality_data['year_month'].astype(str)
        seasonality_data['year_month'] = pd.to_datetime(seasonality_data['year_month'], format="%Y-%m")

        # Create the line chart
        fig = px.line(
            seasonality_data,
            x='year_month',
            y='ROI_seasonal_adjusted',
            color='marketing_channel',
            title="Seasonal ROI Over Time by Marketing Channel",
            labels={
                "year_month": "Date",
                "ROI_seasonal_adjusted": "Seasonal Adjusted ROI",
                "marketing_channel": "Marketing Channel"
            }
        )

        # Update layout for better readability
        fig.update_layout(
            xaxis=dict(title="Date"),
            yaxis=dict(title="Seasonal Adjusted ROI"),
            margin=dict(l=40, r=40, t=40, b=80),
            xaxis_tickformat="%b %Y"  # Format for month and year (e.g., Jan 2019)
        )

        max_roi = seasonality_data['ROI_seasonal_adjusted'].max()
        max_date = seasonality_data.loc[seasonality_data['ROI_seasonal_adjusted'].idxmax(), 'year_month']
        fig.add_annotation(
            x=max_date,
            y=max_roi,
            text=f"Peak ROI: {max_roi:.2f}",
            showarrow=True,
            arrowhead=1
        )
    tab3.plotly_chart(fig)

def display_tab3c(tab3, sales_data):
    with tab3:
        # Section Title
        st.subheader("Overall Impact of Promotional Campaigns on Sales")

        # Dropdown selection for chart type
        chart_type = st.selectbox(
            "Select Chart Type",
            options=[
                "Total quantity sold",
                "Average quantity sold per transaction",
                "Total revenue",
                "Average revenue per transaction",
                "Total transactions",
                "Repeat purchase rate",
                "Product variety per transaction",
                "New customer rate",
                "Average adjusted ROI"
            ]
        )

        # Initialize variables based on chart type
        if chart_type == "Total quantity sold":
            data = sales_data.groupby("coupon_status")['quantity'].sum().reset_index()
            y_axis = "quantity"
            title = "Total Quantity Sold"
        elif chart_type == "Average quantity sold per transaction":
            data = sales_data.groupby("coupon_status")['quantity'].mean().reset_index()
            y_axis = "quantity"
            title = "Average Quantity Sold per Transaction"
        elif chart_type == "Total revenue":
            data = sales_data.groupby("coupon_status")['revenue'].sum().reset_index()
            y_axis = "revenue"
            title = "Total Revenue"
        elif chart_type == "Average revenue per transaction":
            data = sales_data.groupby("coupon_status")['revenue'].mean().reset_index()
            y_axis = "revenue"
            title = "Average Revenue per Transaction"
        elif chart_type == "Total transactions":
            data = sales_data.groupby("coupon_status")['transaction_id'].nunique().reset_index()
            y_axis = "transaction_id"
            title = "Total Transactions"
        elif chart_type == "Repeat purchase rate":
            data = sales_data.groupby("coupon_status")['Is_First_Purchase'].apply(lambda x: 1 - x.mean()).reset_index()
            y_axis = "Is_First_Purchase"
            title = "Repeat Purchase Rate"
        elif chart_type == "Product variety per transaction":
            data = sales_data.groupby("coupon_status")['product_id'].nunique().reset_index()
            y_axis = "product_id"
            title = "Product Variety per Transaction"
        elif chart_type == "New customer rate":
            data = sales_data.groupby("coupon_status")['Is_First_Purchase'].mean().reset_index()
            y_axis = "Is_First_Purchase"
            title = "New Customer Rate"
        elif chart_type == "Average adjusted ROI":
            data = sales_data.groupby("coupon_status")['ROI_adjusted'].mean().reset_index()
            y_axis = "ROI_adjusted"
            title = "Average Adjusted ROI"
        
        fig = px.bar(
            data,
            x="coupon_status",
            y=y_axis,
            title=title,
            labels={"coupon_status": "Coupon Status", y_axis: title},
            color_discrete_sequence=["#1f77b4"]
        )
    tab3.plotly_chart(fig)

def display_tab3d(tab3, sales_data):
    with tab3:
        # Section Title
        st.subheader("Impact of Different Promotional Campaigns on Sales")

        # Dropdown selection for chart type
        chart_type = st.selectbox(
            "Select Chart Type",
            options=[
                "Total quantity sold",
                "Average quantity sold per transaction",
                "Total revenue",
                "Average revenue per transaction",
                "Total transactions",
                "Repeat purchase rate",
                "Product variety per transaction",
                "New customer rate",
                "Average Adjusted ROI"
            ],
            key="chart_type_selector_tab3d"  # Unique key to avoid duplicate ID error
        )

        # Initialize variables based on chart type
        if chart_type == "Total quantity sold":
            data = sales_data.groupby(["coupon_code", "coupon_status"])['quantity'].sum().reset_index()
            y_axis = "quantity"
            title = "Total Quantity Sold"
        elif chart_type == "Average quantity sold per transaction":
            data = sales_data.groupby(["coupon_code", "coupon_status"])['quantity'].mean().reset_index()
            y_axis = "quantity"
            title = "Average Quantity Sold per Transaction "
        elif chart_type == "Total revenue":
            data = sales_data.groupby(["coupon_code", "coupon_status"])['revenue'].sum().reset_index()
            y_axis = "revenue"
            title = "Total Revenue"
        elif chart_type == "Average revenue per transaction":
            data = sales_data.groupby(["coupon_code", "coupon_status"])['revenue'].mean().reset_index()
            y_axis = "revenue"
            title = "Average Revenue per Transaction"
        elif chart_type == "Total transactions":
            data = sales_data.groupby(["coupon_code", "coupon_status"])['transaction_id'].nunique().reset_index()
            y_axis = "transaction_id"
            title = "Total Transactions"
        elif chart_type == "Repeat purchase rate":
            data = sales_data.groupby(["coupon_code", "coupon_status"])['Is_First_Purchase'].apply(lambda x: 1 - x.mean()).reset_index()
            y_axis = "Is_First_Purchase"
            title = "Repeat Purchase Rate"
        elif chart_type == "Product variety per transaction":
            data = sales_data.groupby(["coupon_code", "coupon_status"])['product_id'].nunique().reset_index()
            y_axis = "product_id"
            title = "Product Variety per Transaction"
        elif chart_type == "New customer rate":
            data = sales_data.groupby(["coupon_code", "coupon_status"])['Is_First_Purchase'].mean().reset_index()
            y_axis = "Is_First_Purchase"
            title = "New Customer Rate"
        elif chart_type == "Average adjusted ROI":
            data = sales_data.groupby(["coupon_code", "coupon_status"])['ROI_adjusted'].mean().reset_index()
            y_axis = "ROI_adjusted"
            title = "Average adjusted ROI"
        
        fig = px.bar(
            data,
            x="coupon_code",
            y=y_axis,
            color="coupon_status",
            barmode="group",
            title=title,
            labels={"coupon_code": "Coupon Code", "coupon_status": "Coupon Status", y_axis: title},
            color_discrete_sequence=["#1f77b4", "#4c78a8"]  # Different shades of blue
        )

        # Update layout to make x-axis scrollable
        fig.update_layout(
            xaxis=dict(
                title="Coupon Code",
                tickangle=-45,
                rangeslider=dict(visible=True),  # Adds a scrollable range slider
                tickmode="linear"
            ),
            yaxis=dict(title=title),
            margin=dict(l=40, r=40, t=40, b=80)
        )

        # Add an annotation to label the range slider
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.5, y=-0.35,  # Position below the plot
            showarrow=False,
            text="Use the slider below to scroll through coupon codes",
            font=dict(size=12, color="grey")
        )
    tab3.plotly_chart(fig)

def display_tab3e(tab3, sales_data):
    with tab3:
        # Section Title
        st.subheader("Market Basket Analysis of Promotional Campaign Products")
        
        basket = sales_data.groupby(['transaction_id', 'product_id'])['quantity'].sum().unstack().reset_index().fillna(0).set_index('transaction_id')
        basket = basket.applymap(lambda x: 1 if x > 0 else 0)

        # Slider for min_support in Streamlit
        min_support = st.slider("Select minimum support threshold", min_value=0.001, max_value=0.020, value=0.005, step=0.001)

        # Generate frequent itemsets and association rules based on min_support
        frequent_itemsets = apriori(basket, min_support=min_support, use_colnames=True)
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.1)

        # List to store rows of data
        association_data = []
        unique_products = basket.columns 

        for product in unique_products:
            product_set = frozenset([product])
            related_rules = rules[rules['antecedents'].apply(lambda x: product_set.issubset(x)) |
                                rules['consequents'].apply(lambda x: product_set.issubset(x))]
            for _, row in related_rules.iterrows():
                association_data.append({
                    'Product': product,
                    'Antecedents': row['antecedents'],
                    'Consequents': row['consequents'],
                    'Support': row['support'],
                    'Confidence': row['confidence'],
                    'Lift': row['lift']
                })

        associations_df = pd.DataFrame(association_data)

        # Create a directed graph
        G = nx.DiGraph()

        for _, row in associations_df.iterrows():
            antecedent_ids = ', '.join([str(p) for p in row['Antecedents']])
            consequent_ids = ', '.join([str(p) for p in row['Consequents']])
            G.add_edge(antecedent_ids, consequent_ids, weight=row['Lift'])

        # Generate node positions with NetworkX
        pos = nx.spring_layout(G, k=1.5, seed=42)

        # Extract node and edge information for Plotly
        edge_x = []
        edge_y = []
        lift_labels_x = []
        lift_labels_y = []
        lift_text = []

        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
            
            # Midpoint for lift label
            lift_labels_x.append((x0 + x1) / 2)
            lift_labels_y.append((y0 + y1) / 2)
            lift_text.append(f"{edge[2]['weight']:.2f}")  # Format lift to 2 decimal places

        # Create edge traces in Plotly
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        # Create node traces with product_id as labels
        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)  # Display product_id as labels

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            marker=dict(
                size=10,
                color='lightblue',
                line_width=2
            ),
            textposition="top center"
        )

        # Create lift label trace
        lift_trace = go.Scatter(
            x=lift_labels_x,
            y=lift_labels_y,
            text=lift_text,
            mode='text',
            textfont=dict(color='blue', size=10),
            hoverinfo='none'
        )

        # Plot the graph with Plotly
        fig = go.Figure(data=[edge_trace, node_trace, lift_trace],
                        layout=go.Layout(
                            showlegend=False,
                            hovermode='closest',
                            title=f"Product Association Network (Minimum Support={min_support:.3f})",
                            title_x=0,
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                        ))
        
        st.write("""
        #### Market Basket Analysis
        - **Blue values** on the edges represent **Lift scores**.
        - **Lift** measures the strength of the association between two products. A lift score greater than 1 suggests that the products are more likely to be bought together (complements), the higher the value, the stronger the association
        """)

    tab3.plotly_chart(fig)


        