# Marketing Channels and Promotional Campaigns Analysis

## Project Objectives
This section aims to find the most effective marketing channels and promotional campaigns. This will be done through exploring the ROI of different marketing channels utilised by Amazon and uncovering the impact of different promotional campaigns launched by Amazon on sales.

## Project Structure

The `marketing_channel` folder contains the following files:

- **`marketing_channels.ipynb`**: Jupyter Notebook with the analysis of ROI across marketing channels and different promotional campaigns
- **`marketing_channels.csv`**: CSV file containing features engineered such as ROI and adjusted ROI for use in our streamlit app

## Approach for Marketing Channel Analysis
To achieve our objective, we will follow these steps:
1. Data Loading and Exploration: Load and explore the provided datasets to understand their structure and basic statistics.
2. Feature Engineering: Extract relevant cost and revenue features from the online sales dataset and create additional features.
3. Synthetic Data Generation: Generate synthetic data on marketing channels as well as ROI multipliers to account for differing channel effectiveness based on research.
4. Visualization: Visualize the ROI of different product categories, marketing channels. Visualise the change in ROI across different marketing channels over time. 
5. Customer Segmentation: Segments customers and identify business solutions for different customer segments according to marketing channels and ROI analysis. 
6. Modelling: Using multinomial logistic regression and random forest classifier to identifier feature importance in determining marketing channel preference.

## Approach for Promotional Campaigns Analysis
To achieve our objective, we will follow these steps:
1. Data Loading and Exploration: Load and explore the provided datasets to understand their structure and basic statistics.
2. Sales Metrics Identification: Determine the various sales metrics to prepare for feature engineering afterwards.
3. Feature Engineering: Extract relevant cost, revenue and coupon features from the online sales dataset and create additional features.
4. Visualization: Visualize the overall and individual impact of promotional campaigns on different sales metrics.
5. Customer Segmentation: Segments customers and identify business solutions for different customer segments according to promotional campaign participation. 
6. Modelling: Using random forest classifier to identifier feature importance in predicting promotional campaign participation.



