-- Create the 'products' table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(500),
    about_product TEXT,
    category VARCHAR(255),
    actual_price NUMERIC(10, 2),
    discounted_price NUMERIC(10, 2),
    discount_percentage NUMERIC(5, 2),
    img_link VARCHAR(500),
    origin_area VARCHAR(50)
);

-- Create the 'ratings' table
CREATE TABLE IF NOT EXISTS ratings (
    product_id VARCHAR(50) REFERENCES products(product_id) ON DELETE CASCADE,
    average_rating FLOAT,
    review_title VARCHAR(1000),
    review_content TEXT,
    rating_count INTEGER
);

-- Create the 'users' table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    age INTEGER,
    gender VARCHAR(50)
);

-- Create the 'user_behaviour' table
CREATE TABLE IF NOT EXISTS user_behaviour (
    timestamp TIMESTAMP,
    purchase_frequency VARCHAR(50),
    purchase_categories VARCHAR(255),
    personalized_recommendation_success VARCHAR(50),
    browsing_frequency VARCHAR(50),
    product_search_method VARCHAR(50),
    search_result_exploration VARCHAR(50),
    customer_reviews_importance CHAR(1),
    add_to_cart_browsing VARCHAR(50),
    cart_completion_frequency VARCHAR(50),
    cart_abandonment_factors VARCHAR(255),
    saveforlater_frequency VARCHAR(50),
    review_left VARCHAR(50),
    review_reliability VARCHAR(50),
    review_helpfulness VARCHAR(50),
    personalized_recommendation_frequency CHAR(1),
    recommendation_helpfulness VARCHAR(50),
    rating_accuracy CHAR(1),
    shopping_satisfaction CHAR(1),
    service_appreciation VARCHAR(255),
    improvement_areas VARCHAR(255),
    user_id INTEGER PRIMARY KEY,
    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);


-- Create the 'online_sales' table
CREATE TABLE IF NOT EXISTS online_sales (
    cust_id INT,
    transaction_id INT,
    date DATE,
    product_id VARCHAR(50),
    coupon_status VARCHAR(50),
    coupon_code VARCHAR(50),
    discount_percentage NUMERIC(5, 2),
    delivery_charges NUMERIC(10, 2),
    quantity INT,
    PRIMARY KEY (cust_id, transaction_id, product_id, coupon_status, coupon_code),
    FOREIGN KEY (cust_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- Create the 'shipping_status' table
CREATE TABLE IF NOT EXISTS shipping_status (
    user_id INT,
    transaction_id INT,
    date DATE,
    product_id VARCHAR(50),
    shipping_id INT PRIMARY KEY,
    status VARCHAR(255),
    fulfilment VARCHAR(50),
    ship_service_level VARCHAR(50),
    estimated_delivery_date DATE,
    fulfilled_by VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- Create the 'shipping_history' table
CREATE TABLE IF NOT EXISTS shipping_history (
    date DATE,
    shipping_id INT,
    status VARCHAR(255),
    ship_service_level VARCHAR(50),
    update_date DATE,
    PRIMARY KEY (shipping_id, status),
    FOREIGN KEY (shipping_id) REFERENCES shipping_status(shipping_id) ON DELETE CASCADE
);

-- Insert data into 'products' table
COPY products(product_id, product_name, about_product, category, actual_price, discounted_price, discount_percentage, img_link, origin_area)
FROM '/docker-entrypoint-initdb.d/products.csv' DELIMITER ',' CSV HEADER;

-- Insert data into 'ratings' table
COPY ratings(product_id, average_rating, review_title, review_content, rating_count)
FROM '/docker-entrypoint-initdb.d/ratings.csv' DELIMITER ',' CSV HEADER;

-- Insert data into 'users' table
COPY users(user_id, age, gender)
FROM '/docker-entrypoint-initdb.d/users.csv' DELIMITER ',' CSV HEADER;

COPY users(user_id, age, gender)
FROM '/docker-entrypoint-initdb.d/online_sales_users.csv' DELIMITER ',' CSV HEADER;

-- Insert data into 'user_behaviour' table
COPY user_behaviour(timestamp, purchase_frequency, purchase_categories, personalized_recommendation_success, browsing_frequency, 
                    product_search_method, search_result_exploration, customer_reviews_importance, add_to_cart_browsing, 
                    cart_completion_frequency, cart_abandonment_factors, saveforlater_frequency, review_left, review_reliability, 
                    review_helpfulness, personalized_recommendation_frequency, recommendation_helpfulness, rating_accuracy, 
                    shopping_satisfaction, service_appreciation, improvement_areas, user_id)
FROM '/docker-entrypoint-initdb.d/user_behaviour.csv' DELIMITER ',' CSV HEADER;

-- Insert data into 'online_sales' table
COPY online_sales(cust_id, transaction_id, date, product_id, coupon_status, coupon_code, discount_percentage, delivery_charges, quantity)
FROM '/docker-entrypoint-initdb.d/online_sales_edited.csv' DELIMITER ',' CSV HEADER;

-- Convert 'date' column in online_sales to proper date format
UPDATE online_sales SET date = TO_DATE(date::text, 'YYYY-MM-DD');

-- Insert data into 'shipping_status' table
COPY shipping_status(user_id, transaction_id, date, product_id, shipping_id, status, fulfilment, ship_service_level, 
                     estimated_delivery_date, fulfilled_by)
FROM '/docker-entrypoint-initdb.d/shipping_status.csv' DELIMITER ',' CSV HEADER;

-- Convert 'date' and 'estimated_delivery_date' columns in shipping_status to proper date format
UPDATE shipping_status SET date = TO_DATE(date::text, 'YYYY-MM-DD');
UPDATE shipping_status SET estimated_delivery_date = TO_DATE(estimated_delivery_date::text, 'YYYY-MM-DD');

-- Insert data into 'shipping_history' table
COPY shipping_history(date, shipping_id, status, ship_service_level, update_date)
FROM '/docker-entrypoint-initdb.d/shipping_history.csv' DELIMITER ',' CSV HEADER;

-- Convert 'date' and 'update_date' columns in shipping_history to proper date format
UPDATE shipping_history SET date = TO_DATE(date::text, 'YYYY-MM-DD');
UPDATE shipping_history SET update_date = TO_DATE(update_date::text, 'YYYY-MM-DD');