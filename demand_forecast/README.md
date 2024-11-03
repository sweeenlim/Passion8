# Demand Forecasting and Inventory Optimisation

## Project Overview
This project aims to optimize inventory levels to minimize costs while ensuring product availability. The approach involves two main components:

Demand Forecasting: Develop a demand forecasting model using historical sales data to predict future demand for products. Accurate demand forecasts are crucial for making informed inventory decisions and avoiding stockouts or overstock situations.

Inventory Optimization: Create an inventory optimization algorithm that balances stock levels and costs. The algorithm will use the demand forecasts to determine the optimal inventory levels, ensuring that products are available when needed while minimizing holding and shortage costs.

By integrating demand forecasting with inventory optimization, the project seeks to enhance inventory management efficiency, reduce costs, and improve customer satisfaction. The notebook includes data preprocessing, model training, evaluation steps, and the implementation of the inventory optimization algorithm to ensure accurate and reliable results.

## Folder Structure
```
demand-forecast/ │ 
├── demand_forecast.ipynb # Jupyter Notebook for demand forecasting 
├── demand_forecasting.py # Python script for demand forecasting 
├── README.md # Project documentation 
├── forecast.csv # CSV file containing forecasted demand data
└── model.txt # Text file containing model details
```

## Objective
The primary objective of this project is to develop a comprehensive system that optimizes inventory levels to minimize costs while ensuring product availability. This involves constructing a machine learning model to accurately predict future demand for various products based on historical sales data. By integrating demand forecasting with an inventory optimization algorithm, retailers will be empowered to make data-driven decisions, optimize inventory management, reduce costs, and effectively meet customer demand.

## Approach
To achieve our objective, we will follow these steps:
1. Data Loading and Exploration: Load and explore the provided datasets to understand their structure and basic statistics.
2. Feature Engineering: Extract relevant time-related features from the date column and create additional features.
3. Lag Features: Generate lag features to capture past sales patterns for time series forecasting.
4. Rolling Mean Features: Apply rolling mean features to smooth sales data and capture trends.
5. Exponential Weighted Moving Averages (EWMA): Use EWMA to give more weight to recent sales data.
6. Model Training: Implement machine learning algorithms like LightGBM, Random Forest and Linear Regression to train the model on historical sales data.
7. Performance Evaluation: Evaluate the model's performance using metrics such as SMAPE (Symmetric Mean Absolute Percentage Error).
8. Prediction Generation: Generate sales forecasts for the test dataset.
9. Visualization: Visualize the forecasted sales and compare them with actual sales to assess the model's effectiveness.

## Usage

### Running the Python Script
```sh
        python demand_forecasting.py --test_data path_to_test_data --model_file model.txt --output_file path_to_output_file
```


