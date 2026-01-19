import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier

# 1. Load the dataset
df = pd.read_csv('C:\\Users\\dm2so\\Desktop\\Major Project\\data science\\data source\\telco_churn_with_all_feedback.csv')

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




from fastapi import FastAPI
import joblib
import pandas as pd
from pydantic import BaseModel

# 1. Initialize FastAPI
app = FastAPI()

# 2. Load the "Brain" you just created
model = joblib.load('churn_model.pkl')
scaler = joblib.load('scaler.pkl')
encoders = joblib.load('label_encoders.pkl')

# 3. Define the Input Format (The Data Contract for Satya)
class CustomerData(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float

@app.post("/predict")
def predict_churn(data: CustomerData):
    # Convert input to DataFrame
    input_df = pd.DataFrame([data.dict()])
    
    # Encode categorical text using your saved encoders
    for col, le in encoders.items():
        if col in input_df.columns:
            input_df[col] = le.transform(input_df[col])
            
    # Scale numerical values
    num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
    input_df[num_cols] = scaler.transform(input_df[num_cols])
    
    # Make Prediction
    prediction = model.predict(input_df)
    probability = model.predict_proba(input_df)[0][1]
    
    return {
        "churn_prediction": int(prediction[0]),
        "probability": round(float(probability), 2),
        "status": "High Risk" if prediction[0] == 1 else "Low Risk"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)