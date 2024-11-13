# Price Elasticity Analysis and Dynamic Pricing Strategy

## Objective
This project aims to explore and implement pricing strategies that maximize revenue by analyzing price elasticity for various product categories and developing a dynamic pricing model based on demand.

## Project Structure
The `price elasticity` folder contains the following files:

- **`price_elasticity.ipynb`**: Jupyter Notebook with the analysis of price elasticity across different product categories.
- **`ped_results.csv`**: CSV file containing price elasticity of demand (PED) estimates for each product category.
- **`forecast_with_ped.csv`**: CSV file that combines demand forecasts, PED results, and product details for use in our streamlit app.

## Approach
To answer the question, "What pricing strategies can we implement to maximize revenue?" the following approach was taken:

### 1. Data Loading and Exploration
   - Initial data loading and examination to understand the structure and contents of the dataset.

### 2. Data Handling
   - For products with missing transaction data:
     - **Sales**: Fill in sales as `0` for any periods without transactions, ensuring each product has consistent sales data for the entire year.
     - **Discount Percentage**: Fill in missing discount percentages based on discount periods, as each discount period has a fixed discount rate for all products.
     - **Data Aggregation**: Aggregate sales data by discount period.

### 3. Feature Engineering
   - Extracted time-based features for use in a log-log regression model to estimate price elasticity.
   - Used 2-month intervals as feature periods (e.g., Jan-Feb as one period, Mar-Apr as another).

### 4. Model Training
   - Implemented a log-log regression model where:
     - **Response Variable**: log(Sales)
     - **Regressors**: Time-based feature and log(`discount_percentage`)
   - The coefficient of log(`discount_percentage`) in this model represents the estimated price elasticity of demand (PED).

### 5. Performance Evaluation
   - Evaluated model performance using the R² value to assess goodness of fit.
   - If the R² value is below 0.5 (indicating a poor fit), set the PED estimate to -1 (assuming unitary elasticity) rather than using the unreliable model output.

### 6. Saving Results
   - Saved the PED estimates to `ped_results.csv`.
   - Combined the PED results with forecast demand data and product details, saving the final output to `forecast_with_ped.csv`.

### 7. Using the Results
- To use the PED result, use the formula $
D = D_{forecast} \times \left(\frac{P_{new}}{P_{no\_discount}}\right)^{PED}$ to obtain the expected demand given the change in price, with $P_{new} = P_{no\_discount} * (1 - discount\_percentage)$. 

## Future Work
To further refine our dynamic pricing model, we can explore:
- A model that takes into account of real-time competitors pricing. 
- Obtain more accurate price elasticity of demand with more data. 
