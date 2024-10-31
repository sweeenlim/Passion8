# AI-Enhanced A/B Testing for Product Listings

## Overview

This project implements an AI-based system that generates multiple versions of product titles and descriptions for A/B testing. The goal is to create an automated pipeline for testing these variations and analyzing their impact on click-through rates (CTR) and conversions.

## Features

- **LLM-Based Generation**: Utilizes a Large Language Model (LLM) GPT-4 to generate multiple versions of product titles and descriptions.
- **Automated Pipeline**: Automates the process of testing these variations and analyzing their performance.
- **Data Storage**: Stores generated product information, clicks in a database for easy retrieval and analysis.

## Folder Structure
```
ab-testing-with-llm/
│
├── images/                     # Directory containing product images 
├── llm.py                      # Main script for generating and inserting LLM-based product titles and descriptions
├── app.py                      # Main script for running website used for A/B Testing
├── README.md                   # Project documentation
```
## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/freedytan/Passion8.git
    cd ab-testing-with-llm
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage
1. **Prepare Data**: Place your product image files in the [`images/`] directory.

2. **Run the Pipeline**:
    ```sh
    python llm.py
    ```

3. **Output**: The script will generate multiple versions of product titles and descriptions, store them in the database, and print a confirmation message.

4. **Run the Web Application**:
    ```sh
    streamlit run app.py
    ```

5.  **Output**: The script will launch a random version of the webpage for A/B testing and the clicks will be logged into the database for further analysis on the click-through rate (CTR).

## Demo


https://github.com/user-attachments/assets/9c16036d-4ce1-436e-8f0c-6b1f85298d2a



## Further Steps

After setting up the AI-Enhanced A/B Testing for Product Listings, the following steps can be taken to expand on the project and enhance its functionality:

**Automate Testing Cycles**:
   - Set up a scheduler (e.g., using `cron` jobs or a cloud-based service) to automate the testing cycles. This can help in continuously generating new variations and running tests without manual intervention.

**Refine LLM Prompts**:
   - Experiment with different prompts in `llm.py` to generate varied and engaging product titles and descriptions. Fine-tuning these prompts can help improve the quality of generated content.


