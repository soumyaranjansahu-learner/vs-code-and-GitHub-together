from fastapi import FastAPI
import sqlite3
import requests

app = FastAPI()

# 1. Initialize the Database
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

# 2. THE NEW BRIDGE ENDPOINT
@app.post("/add-customer")
def add_customer(name: str, tenure: int, monthly_charges: float):
    # This prepares the data for the AI service on port 8000
    ai_url = "http://127.0.0.1:8000/predict"
    
    # We send a sample payload (ensure this matches your model's expected fields)
    sample_payload = {
        "gender": "Male", "SeniorCitizen": 0, "Partner": "No", "Dependents": "No",
        "tenure": tenure, "PhoneService": "Yes", "MultipleLines": "No",
        "InternetService": "DSL", "OnlineSecurity": "No", "OnlineBackup": "No",
        "DeviceProtection": "No", "TechSupport": "No", "StreamingTV": "No",
        "StreamingMovies": "No", "Contract": "Month-to-month", "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check", "MonthlyCharges": monthly_charges, "TotalCharges": monthly_charges * tenure
    }

    # Call the AI service
    try:
        response = requests.post(ai_url, json=sample_payload)
        prediction = response.json()
        
        # Save to your SQLite Database
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
    
    

@app.get("/get-all-customers")
def get_all_customers():
    conn = sqlite3.connect('customers.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    # Format the data into a list of dictionaries for the Frontend
    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "name": row[1],
            "tenure": row[2],
            "monthly_charges": row[3],
            "risk_status": row[4],
            "probability": row[5]
        })
    return result