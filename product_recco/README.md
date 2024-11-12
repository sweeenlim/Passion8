
# E-Commerce Product Recommendation System

This repository contains a traditional product recommendation system for e-commerce users, to answer the group B task in the project. The system is designed to provide personalized product recommendations by combining multiple recommendation strategies, including user-based collaborative filtering, content-based filtering, and cold-start recommendations.

## Table of Contents
- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [Recommendation Strategies](#recommendation-strategies)
- [Overall Recommendation Engine](#overall-recommendation-engine)
- [Evaluation](#evaluation)

---

## Features
- **User-Based Collaborative Filtering**: Recommends products based on similarities between users' purchasing behaviors.
- **Content-Based Filtering**: Recommends products based on content similarities with previously purchased items.
- **Cold-Start Recommendations**: Provides popular recommendations for new users who lack interaction history.

## Setup

### Prerequisites
- **Python 3.12.4**
- **Virtual Environment**: Recommended for dependency management.

Load environment variables from a `.env` file (create this file if it doesn't exist) in the parent directory with the following variables:
   ```plaintext
   POSTGRES_PASSWORD=your_postgres_password
   POSTGRES_PORT_NO=your_postgres_port
   POSTGRES_HOST=your_postgres_host
   POSTGRES_DB=your_postgres_db
   POSTGRES_USER=your_postgres_user
   ```

## Usage

```python
# Initialize the recommendation system
overall_recommendation(user_id=12583, transactions_df=df, products_df=products, top_n=5)
```

## Recommendation Strategies

1. **User-Based Collaborative Filtering**: 
   - Recommends products by finding similar users and suggesting products based on their purchasing patterns.
   - Uses cosine similarity to measure similarity between users.

2. **Content-Based Filtering**:
   - Recommends products by analyzing product features and suggesting similar products based on text descriptions.
   - Uses TF-IDF and cosine similarity to evaluate similarity between product descriptions.

3. **Cold-Start Recommendations**:
   - Suggests popular products for new users with no purchase history.
   - Offers recommendations based on overall product popularity.

## Overall Recommendation Engine

The `overall_recommendation` function integrates the strengths of all three strategies to provide balanced and personalized recommendations. It assigns higher weights to user-based recommendations (to make it more personalised) and includes content-based recommendations to handle product diversity. Cold-start recommendations are used for new users to mitigate the cold-start problem.


## Evaluation
Evaluation of the recommendation system is not included in this project. To accurately assess the performance of the recommendations, we would prefer to use real-world company data, which reflects actual user behavior and purchasing trends which we do not have at the moment. Using authentic data enables a more precise evaluation of recommendation quality and relevance. Future works could include this approach providing a better measure of the system's effectiveness and impact substantiated by relevant up-to-date data.