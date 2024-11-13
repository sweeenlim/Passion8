# AI Generated Personalized Email Marketing Campaigns

This section contains a personalised email generating system for e-commerce users. The system is designed to generate personalised marketing email to customers who have recently made a transaction by combining multiple recommendation strategies, including user-based collaborative filtering, content-based filtering, and cold-start recommendations.

## Table of Contents
- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [Acknowledgements](#acknowledgements)

---

## Features
- **Retrieval-Augmented Generation (RAG)**: Uses H2O GPT's RAG model for email generation and enhanced product description.
- **Session Management**: Maintains chat history using Streamlit's session state.

## Setup

### Prerequisites
- **Python 3.12.4**
- **Virtual Environment**: Recommended for dependency management.
- **H2O GPT API Key and Collection ID**: Required for connecting to H2O GPT's RAG model.


### Environment Variables
Create a `.env` file in the parent directory with the following environment variables:

```plaintext
H2O_API_KEY_EMAIL=your_h2o_api_key
H2O_PRODUCTS_COLLECTION_ID=your_h2o_collection_id
```

- `H2O_API_KEY_EMAIL`: Your H2O GPT API key.
- `H2O_PRODUCTS_COLLECTION_ID`: The collection ID for the product collection to retrieve recommendations from.

## Usage

1. Run the Streamlit application:
   ```bash
   streamlit run Hello.py
   ```

2. Open the link displayed in your terminal to access the application (usually `http://localhost:8501`).

3. From the drop-down box, select a user from the catalogue of users who have recently made a purchase. Click on "Generate Email" to see the persoanlised marketing email content for the selected user.

## Acknowledgements
- [H2O.ai](https://www.h2o.ai/) for providing the H2O GPT API and RAG capabilities.