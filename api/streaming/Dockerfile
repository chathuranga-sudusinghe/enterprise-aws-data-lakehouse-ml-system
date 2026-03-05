FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y gcc g++ libgomp1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only what consumer needs
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the API package so "python -m api.streaming.consumer" works
COPY api /app/api
COPY ml /app/ml

CMD ["python", "-m", "api.streaming.consumer"]