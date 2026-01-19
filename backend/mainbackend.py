from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import requests

# 1. Define the App ONLY ONCE
app = FastAPI()

# 2. Add CORS Middleware (Crucial for Sai's Frontend to work)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Initialize the Database
def init_db():
    conn = sqlite3.connect('customers.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            tenure INTEGER,
            monthly_charges REAL,
            risk_status TEXT,
            probability REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.get("/Home")
def home():
    return {"message": "Backend Service is Running"}

# 4. The Bridge Endpoint (Satya's Logic)
@app.post("/add-customer")
def add_customer(name: str, tenure: int, monthly_charges: float):
    ai_url = "http://127.0.0.1:8000/predict"
    
    sample_payload = {
        "gender": "Male", "SeniorCitizen": 0, "Partner": "No", "Dependents": "No",
        "tenure": tenure, "PhoneService": "Yes", "MultipleLines": "No",
        "InternetService": "DSL", "OnlineSecurity": "No", "OnlineBackup": "No",
        "DeviceProtection": "No", "TechSupport": "No", "StreamingTV": "No",
        "StreamingMovies": "No", "Contract": "Month-to-month", "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check", "MonthlyCharges": monthly_charges, 
        "TotalCharges": monthly_charges * tenure
    }

    try:
        response = requests.post(ai_url, json=sample_payload)
        prediction = response.json()
        
        conn = sqlite3.connect('customers.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customers (name, tenure, monthly_charges, risk_status, probability)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, tenure, monthly_charges, prediction['status'], prediction['probability']))
        conn.commit()
        conn.close()
        
        return {"status": "Success", "saved_data": prediction}
    except Exception as e:
        return {"status": "Error", "detail": str(e)}

# 5. Dashboard Endpoint (Sai's Data Source)
@app.get("/get-all-customers")
def get_all_customers():
    conn = sqlite3.connect('customers.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        result.append({
            "id": row[0], "name": row[1], "tenure": row[2],
            "monthly_charges": row[3], "risk_status": row[4], "probability": row[5]
        })
    return result