from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_predict_endpoint():

    sample_request = {
     "data": {
        "TransactionDT": 86400,
        "TransactionAmt": 100.0,
        "card1": 1234,
        "card2": 111,
        "card3": 150,
        "card4": "visa",
        "addr1": 100
      }
    }

    response = client.post("/predict", json=sample_request)

    assert response.status_code == 200
    assert "fraud_prediction" in response.json()
    assert "fraud_probability" in response.json()