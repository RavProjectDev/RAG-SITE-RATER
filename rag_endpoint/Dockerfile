FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# ✅ Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy project files
COPY rag_endpoint /app/rag_endpoint
COPY shared /app/shared

# ✅ Set PYTHONPATH for module resolution
ENV PYTHONPATH=/app

# ✅ Start the app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "rag_endpoint.rav_api.app:app"]
