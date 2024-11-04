# Computer Vision Techniques to enhance Product Search and Discovery 

## Overview

This project implements 2 features.
1. Image-based search feature for visually similar products
2. Automatic Product Categorisation based on image features

## Folder Structure
```
computer_vision/
│
├── amazon_embeddings.csv/      # csv containing all image embeddings of all amazon product images
├── knn_picke_file              # Pickle file containing trained KNN model on all image embeddings
├── images_aug_2k_link          # Link to the google drive containing all 2000 augmented images for image classification model training
├── model.json                  # json file containing CNN model configuration
├── model.weights.h5            # Containing model weights of trained CNN model
├── images_aug_2k_link          # Link to the google drive containing all 2000 augmented images for model training
├── computer_vision.ipynb       # Jupyter notebook containing all workins for data preparation and model training
├── README.md                   # Project documentation
```
