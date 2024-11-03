import pandas as pd
import numpy as np
import lightgbm as lgb
import argparse

def get_model_features(model_file):
    """
    Load a pre-trained LightGBM model from a file and return its feature names.
    
    Parameters:
    - model_file (str): Path to the pre-trained LightGBM model file.
    
    Returns:
    - feature_names (list): List of feature names used in the model.
    """
    # Load the pre-trained model
    model = lgb.Booster(model_file=model_file)
    
    # Get feature names
    feature_names = model.feature_name()
    
    return feature_names

def compare_features(model_features, test_df):
    """
    Compare the features used in the model with the features in the test data.
    
    Parameters:
    - model_features (list): List of feature names used in the model.
    - test_df (pd.DataFrame): Test data containing the features.
    
    Returns:
    - missing_features (list): List of features missing in the test data.
    - extra_features (list): List of extra features in the test data.
    """
    test_features = test_df.columns.tolist()
    
    missing_features = [feature for feature in model_features if feature not in test_features]
    extra_features = [feature for feature in test_features if feature not in model_features]
    return missing_features, extra_features


def feature_engineering(df,lags=[7, 14, 30, 60, 90],alphas=[0.99, 0.95, 0.9, 0.8, 0.7, 0.5]):
    """
    Apply feature engineering to the df.
    
    Parameters:
    - df (pd.df): df containing the data.
    
    Returns:
    - df (pd.df): df with engineered features.
    """
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df.date.dt.month
    df['day_of_month'] = df.date.dt.day
    df['day_of_year'] = df.date.dt.dayofyear
    df['week_of_year'] = df.date.dt.isocalendar().week
    df['day_of_week'] = df.date.dt.dayofweek
    df["is_wknd"] = df.date.dt.weekday // 4
    df['is_month_start'] = df.date.dt.is_month_start.astype(int)
    df['is_month_end'] = df.date.dt.is_month_end.astype(int)
        
    for lag in lags:
        df['sales_lag_' + str(lag)] = df.groupby(["product_id"])['sales'].transform(
            lambda x: x.shift(lag)) + np.random.normal(scale=1.6, size=(len(df),))
        df['sales_roll_mean_' + str(lag)] = df.groupby(["product_id"])['sales']. \
                                                          transform(lambda x: x.shift(1).rolling(window=lag, min_periods=min(lag,10), win_type="triang").mean()) + np.random.normal(scale=1.6, size=(len(df),))
    for alpha in alphas:
        for lag in lags:
            df['sales_ewm_alpha_' + str(alpha).replace(".", "") + "_lag_" + str(lag)] = \
                df.groupby(["product_id"])['sales'].transform(lambda x: x.shift(lag).ewm(alpha=alpha).mean())
    df = pd.get_dummies(df, columns=['day_of_week', 'month'])
    df['sales'] = np.log1p(df["sales"].values)
    return df

def load_model_and_predict(model_file, test_df):
    """
    Load a pre-trained LightGBM model from a file and make predictions on the test data.
    
    Parameters:
    - model_file (str): Path to the pre-trained LightGBM model file.
    - test_df (pd.DataFrame): Test data containing 'date' and 'product_id' columns.
    
    Returns:
    - test_df (pd.DataFrame): DataFrame containing the test data with predictions.
    """
    # Load the pre-trained model
    model = lgb.Booster(model_file=model_file)
    
    # Apply feature engineering to the test data
    test_df = feature_engineering(test_df)
    
    # Prepare the test data for prediction
    test_features = test_df.drop(columns=['sales','date'], errors='ignore')
    
    # Make predictions
    test_df['sales'] = model.predict(test_features)

    # Inverse log transformation
    test_df['sales'] = np.expm1(test_df['sales'])

    # Keep only the required columns
    test_df = test_df[['date', 'product_id', 'sales']]
    
    return test_df

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Predict sales for a specific date using a pre-trained LightGBM model.')
    parser.add_argument('--test_data', type=str, required=True, help='Path to the test data CSV file.')
    parser.add_argument('--model_file', type=str, required=True, help='Path to the pre-trained LightGBM model file.')
    parser.add_argument('--output_file', type=str, required=True, help='Path to the output CSV file to save predictions.')

    # Parse arguments
    args = parser.parse_args()

    # Load test data
    test_df = pd.read_csv(args.test_data)
    
    # Load the model and make predictions
    predictions_df = load_model_and_predict(args.model_file, test_df)
    
    # Save the predictions to a CSV file
    predictions_df.to_csv(args.output_file, index=False)