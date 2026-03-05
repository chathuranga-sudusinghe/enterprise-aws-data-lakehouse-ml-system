import pandas as pd

def test_data_schema():

    df = pd.DataFrame({
        "TransactionAmt":[100,200],
        "card1":[1234,2345]
    })

    required_columns = ["TransactionAmt","card1"]

    for col in required_columns:
        assert col in df.columns