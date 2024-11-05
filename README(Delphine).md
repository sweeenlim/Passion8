# What are the key factors influencing customer purchasing behavior?

This project analyzes historical sales data to identify patterns and trends that influence customer purchasing behavior. It aims to develop customer segmentation models based on these insights, allowing for targeted marketing strategies and improved customer engagement.

## 1. Analyze historical sales data to identify patterns and trends.

### Data Manipulation
1. **Total Price Calculation**:
    - A `total_price` column was created based on `coupon_status`:
    - If a coupon was used, `total_price = actual_price × (1 - discount_pct) × quantity`.
    - Otherwise, `total_price = actual_price × quantity`.

2. **Category Hierarchy**:
    - Renamed `category` to `subcategory`.
    - Added a `category` column to represent overarching categories (e.g., “Home & Kitchen” for subcategories like "Heating, Cooling & Air Quality").

### Exploratory Data Analysis
1. **Ratings Analysis**:
   - Analyzed the distribution of ratings across productsand discovered that most products had a rating frequency of at least 1000.

2. **Coupon and Discount Analysis**:
   - Majority of coupons were observed to be unused, indicating that customers may not be aware of the coupons available.
   - Discount percentages followed a normal distribution and had no strong correlation with actual price.

3. **Historical Sales Analysis**
    - Daily and Monthly plots of total sales reveals peaks in March, April, June, July and August, which coincides with exceptionally large transactions (total_price > 200,000 USD). 
    
![Alt text](images/daily_sales.png) 

![Alt text](images/monthly_sales.png)

   - The 'Electronics' category was the top contributor to total sales, driving total sales throughout the year.

![Alt text](images/monthly_sales_category.png)

   - We found that young adults aged 26-35 years old spend the most compared to other age groups.

![Alt text](images/total_sales_age.png)
   
   - A correlation matrix revealed low inter-feature correlations, affirming the independence of factors influencing sales.

![Alt text](images/correlation.png)
 
## 2. Develop Customer Segmentation Models Based on Purchasing Behavior

### RFM (Recency, Frequency, Monetary) Analysis

RFM Analysis is used to categorize customers based on three criteria:

- **Recency**: Days since the last purchase.
- **Frequency**: Total number of purchases within 2019.
- **Monetary**: Total purchase value within 2019.

Each customer received a score from 1 to 5 for Recency, Frequency, and Monetary metrics. The sum of these scores created an **RFM score**.
- **RFM Segments**: 
   - Low (2-5), Medium (6-8), High (9-11), and Top (12-15).

**Insights**:
- Most customers fall within the High and Top segments, highlighting frequent buyers with recent purchases and high spending.
- These high-value segments are likely responsible for a large portion of revenue; thus, focusing on loyalty programs and exclusive deals for them may sustain engagement.

![Alt text](images/RFM.png)

### CLTV (Customer Lifetime Value) Model

CLTV estimates the projected revenue a customer will bring over their lifecycle:

- **CLTV Formula**: 
   CLTV = ((Average Order Value x Purchase Frequency) / Churn Rate) x Profit margin 

- **Components**:
   - **Average Order Value**: Total revenue divided by the number of orders.
   - **Purchase Frequency**: Total orders divided by total customers.
   - **Churn Rate**: Ratio of customers with no repeat orders.
   - **Profit Margin**: Set to 20%, based on Amazon seller average margins.

**CLTV Segments**:
- Customers were segmented into CLTV categories: Low, Medium, High, and Top.
**Insights**:
- A majority of customers have a high CLTV (≥ 10,000 USD), with 26.9% achieving very high CLTVs of over half a million USD, demonstrating a valuable customer base.

![Alt text](images/cltv_bar.png)

![Alt text](images/cltv_pie.png)

## References

- Profit margin: [Amazon Profit Margin](https://www.sellerapp.com/blog/amazon-profit-margin/)