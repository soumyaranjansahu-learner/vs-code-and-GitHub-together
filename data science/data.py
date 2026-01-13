import pandas as pd

# Load the dataset
df = pd.read_csv('C:\\Users\\dm2so\\Desktop\\Major Project\\data science\\data_ecommerce_customer_churn.csv')

# Look at the first 5 rows
print(df.head())

# Check the column names and data types
print(df.info())

# 1. Check for missing values
print(df.isnull().sum())

# 2. Check the balance (how many churned vs. stayed)
print(df['Churn'].value_counts())