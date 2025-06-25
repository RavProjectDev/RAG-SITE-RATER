FROM python:3.11-slim

WORKDIR /rav_api
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["gunicorn", "-b", "0.0.0.0:5000", "wsgi:rav_endpoint."]
