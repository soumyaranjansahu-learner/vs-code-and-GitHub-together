import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier

# 1. Load the dataset
df = pd.read_csv('telco_churn_with_all_feedback.csv')

# 2. Cleaning: Remove ID and text-heavy feedback columns
df = df.drop(columns=['customerID', 'PromptInput', 'CustomerFeedback'])

# 3. Fix 'TotalCharges' (it has empty spaces that need to be numbers)
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df['TotalCharges'] = df['TotalCharges'].fillna(df['TotalCharges'].median())

# 4. Encoding: Convert text (Female/Male, Yes/No) into numbers
label_encoders = {}
for col in df.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# 5. Split data into Features (X) and Target (y)
X = df.drop('Churn', axis=1)
y = df['Churn']

# 6. Scaling: Normalize large numbers (Charges) so they don't bias the model
scaler = StandardScaler()
num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
X[num_cols] = scaler.fit_transform(X[num_cols])

# 7. Train the Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 8. EXPORT: Save these files for Mahesh and Satya
joblib.dump(model, 'churn_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(label_encoders, 'label_encoders.pkl')

print("Success! Model and Scalers saved. You are ready to build the API.")