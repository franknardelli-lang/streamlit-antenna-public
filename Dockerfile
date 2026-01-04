FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run injects the PORT environment variable (default 8080)
# We configure Streamlit to listen on this port and allow external access
CMD sh -c 'streamlit run Home.py --server.port=${PORT:-8501} --server.address=0.0.0.0'