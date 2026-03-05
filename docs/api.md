# Fraud Detection API

## Overview

The Fraud Detection API provides a REST interface for accessing the trained fraud detection model.

The API is built using **FastAPI** and serves real-time fraud predictions.

---

## Base URL

http://127.0.0.1:8000

---

## Endpoints

### Root Endpoint

GET /

Response:

{
  "message": "Fraud API is running"
}

---

### Health Check

GET /health

Response:

{
  "status": "healthy"
}

---

### Fraud Prediction

POST /predict

Request body:

{
  "data": {
    "TransactionID": 86400,
    "TransactionAmt": 100,
    "card1": 1234,
    "card2": 111,
    "card3": 150,
    "card4": "visa",
    "addr1": 315
  }
}

Response:

{
  "fraud_probability": 0.1641,
  "fraud_prediction": 1
}

---

## Monitoring

The API exposes monitoring metrics through:

GET /metrics

This endpoint provides **Prometheus-compatible metrics** including:

- API request count
- API latency
- system metrics

---

## Logging

Prediction events are recorded in:

artifacts/metrics/api_metrics.jsonl

Each record contains:

- timestamp
- endpoint
- fraud probability
- prediction result