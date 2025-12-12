# Dockerfile for Financial Data Processing System
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY data_set_1.json data_set_2.json load_data.py ./

# Initialize database and load data on container start
CMD python -c "from app.database import init_db; init_db()" && \
    python load_data.py && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000


