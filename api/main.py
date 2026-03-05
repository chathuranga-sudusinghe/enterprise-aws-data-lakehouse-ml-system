from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import logging

# Prometheus monitoring
from prometheus_client import make_asgi_app, Counter, Histogram
import time

from ml.inference.predict import FraudPredictor
from artifacts.metrics.metrics_file_logger import log_api_metric

# -----------------------------
# Logging Configuration
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------
# App Initialization
# -----------------------------
app = FastAPI(title="Fraud Detection API")


# -----------------------------
# Prometheus Metrics
# -----------------------------
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total API requests"
)

REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds",
    "API request latency"
)

# expose /metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# -----------------------------
# Load Model at Startup
# -----------------------------
predictor = FraudPredictor()


# -----------------------------
# Input Schema
# -----------------------------
class TransactionInput(BaseModel):
    data: dict


# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
def root():
    return {"message": "Fraud API is running"}


# -----------------------------
# Health Endpoint
# -----------------------------
@app.get("/health")
def health():
    return {"status": "healthy"}


# -----------------------------
# Prediction Endpoint
# -----------------------------
@app.post("/predict")
def predict(transaction: TransactionInput):
    start_time = time.time()

    try:
        logger.info("Received prediction request")

        REQUEST_COUNT.inc()

        df = pd.DataFrame([transaction.data])
        result = predictor.predict(df)

        response = {
            "fraud_probability": float(result["fraud_probability"].iloc[0]),
            "fraud_prediction": int(result["fraud_prediction"].iloc[0]),
        }

        # File-based metrics logging
        log_api_metric({
            "endpoint": "/predict",
            "fraud_probability": response["fraud_probability"],
            "fraud_prediction": response["fraud_prediction"],
        })

        latency = time.time() - start_time
        REQUEST_LATENCY.observe(latency)

        logger.info("Prediction successful")
        return response

    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction error")