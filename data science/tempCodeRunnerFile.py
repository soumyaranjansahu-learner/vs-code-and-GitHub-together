import pandas as pd

# Load the dataset
df = pd.read_csv('C:\\Users\\dm2so\\Desktop\\Major Project\\data science\\data_ecommerce_customer_churn.csv')

# Look at the first 5 rows
print(df.head())

# Check the column names and data types
print(df.info())