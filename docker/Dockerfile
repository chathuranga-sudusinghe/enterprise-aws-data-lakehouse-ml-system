FROM python:3.11-slim

# Install system dependencies required by LightGBM
RUN apt-get update && \
    apt-get install -y gcc g++ libgomp1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]