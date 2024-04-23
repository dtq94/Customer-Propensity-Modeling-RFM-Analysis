# Customer Propensity Modeling: RFM Analysis

## Business Objective
A client, an early-stage e-commerce company, aims to increase purchases by sending targeted discounts or coupons to users. To optimize their limited funds for discount campaigns, they seek to predict the purchase probability of each user using propensity modeling. This approach helps in identifying users likely to make a purchase, thus reducing costs and increasing ROI. Additionally, RFM (Recency, Frequency, Monetary value) modeling is employed to segment users and personalize marketing strategies.

## Aim
1. Understand Propensity Modeling.
2. Understand RFM Analysis.
3. Build a model to predict the purchase probability of each user in buying a product for an e-commerce company using the propensity model.

## Tech Stack
- Language: Python
- Libraries:
  - pandas
  - sklearn
  - numpy
  - seaborn
  - datetime
  - matplotlib
  - missingno

## Approach
1. **Importing Required Libraries and Packages**: Set up the Python environment with necessary packages.
2. **Read the CSV File**: Load the dataset containing purchase history.
3. **Data Preprocessing**: Handle missing values, clean data, and format fields.
4. **Exploratory Data Analysis (EDA)**:
   - Perform univariate and multivariate analysis to gain insights into the data.
5. **RFM Analysis**:
   - Calculate Recency, Frequency, and Monetary value metrics for customer segmentation.
6. **Feature Engineering**: Create additional features from existing data to improve model performance.
7. **Modeling Data Creation**: Prepare data for modeling by encoding categorical variables and splitting into train/test sets.
8. **Model Building**: Utilize propensity modeling techniques such as Logistic Regression, Random Forest, or Gradient Boosting to predict purchase probability.
9. **Making Predictions**: Use the trained model to predict purchase probabilities for users.

## Project Structure
```
|-- InputFiles
    -- data.csv
|-- SourceFolder
    |-- ML_Pipeline
        -- feature_eng.py
        -- model.py
        -- pre_processing.py
        -- rfm.py
        -- utils.py
    |-- Engine.py
