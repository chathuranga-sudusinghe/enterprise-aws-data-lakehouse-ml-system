from fastapi import FastAPI
from pydantic import BaseModel
from app.inference import predict

app = FastAPI(title="Fraud Detection API")

# ----------------------------------
# Health Check
# ----------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# ----------------------------------
# Prediction Schema
# ----------------------------------
class Transaction(BaseModel):
    # Example fields — must match your dataset
    TransactionDT: int
    TransactionAmt: float
    ProductCD: str
    card1: int
    card2: float | None = None
    card3: float | None = None
    card4: str | None = None
    card5: float | None = None
    card6: str | None = None
    addr1: float | None = None
    # You will later expand this fully

@app.post("/predict")
def predict_fraud(transaction: Transaction):
    result = predict(transaction.dict())
    return result