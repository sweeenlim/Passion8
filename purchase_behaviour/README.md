# Customer Behaviour Analysis and VIP Customer Prediction

Customer Behaviour Analysis: This project analyzes historical sales data to identify patterns and trends that influence customer purchasing behavior. It aims to develop customer segmentation models based on these insights, allowing for targeted marketing strategies and improved customer engagement. 

VIP Customer Prediction: Implement BG-NBD and Gamma-Gamma models to calculate CLTV, segmentizing and identifying valuable customers based on their purchasing frequency and expenditure.

## Objectives
The primary objective of this project is to identify the key factors influencing customer purchasing behavior by analyzing historical sales data. In addition, we seek to segment customers based on their purchasing behaviors to identify VIP customers—those who demonstrate high value to the business. Through techniques like RFM (Recency, Frequency, Monetary) analysis and CLTV (Customer Lifetime Value) prediction, we can categorize customers into meaningful groups, with VIP customers representing top segments. 

## Folder Structure
Here is an overview of the folder structure:
- README.md: Project documentation
- purchase_behaviour.ipynb: Jupyter notebook for customer behaviour analysis and segmentation
- vip_prediction.ipynb: Jupyter notebook for vip prediction (Bonus)
- purchase_behaviour.py: Python script for both purchase_behaviour.ipynb and vip_prediction.ipynb

## Approach
**purchase_behaviour.ipynb**
1. Data Loading: Combined the different tables into one large table, online_sales.
2. Feature Engineering: Created several new columns based on existing features for clearer interpretation and analysis.
3. Exploratory Data Analysis (EDA): 
- Generated basic statistics to understand the data distribution and identify patterns for several features. 
- Created historical plots for metrics like daily and monthly sales and analyzed correlation between features.
4. Model Selection and Training:
- Selected segmentation techniques like RFM (Recency, Frequency, Monetary) and CLTV (Customer Lifetime Value) analysis to group customers based on purchasing behavior.
- Conducted CLTV predictive modeling using linear regression and random forest.
5. Model Evaluation: Evaluate the performance of the model using R-squared value.

**vip_prediction.ipynb (Bonus)** 
1. Data Loading
2. Prediction Model: 
- Implemented the BG-NBD Model to predict the number of purchases a customer will make in the future over a specified period
- Implemented the Gamma-Gamma submodel to predict the monetary value of customer transactions, given that the customer is active. 
3. VIP Customer Identification
- By multiplying the frequency of future transactions (from the BG/NBD model) with the expected transaction value (from the Gamma-Gamma model), we can predict each customer’s lifetime value to obtain VIP customers