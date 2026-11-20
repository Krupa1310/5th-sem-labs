# ---- Sample application image (Flask, port 5000) ----
FROM python:3.12-slim

# Don't buffer stdout so `kubectl logs` shows lines immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

EXPOSE 5000
CMD ["python", "app.py"]
