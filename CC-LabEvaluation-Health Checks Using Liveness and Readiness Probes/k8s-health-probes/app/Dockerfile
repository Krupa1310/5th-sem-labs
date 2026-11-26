# ---- Student Management + health-probe application image (Flask, port 5000) ----
FROM python:3.12-slim

# Don't buffer stdout so `kubectl logs` shows lines immediately
ENV PYTHONUNBUFFERED=1 \
    DB_PATH=/data/students.db

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py students.py ./
COPY static ./static

# /data is where the PersistentVolumeClaim is mounted in Kubernetes
RUN mkdir -p /data
EXPOSE 5000
CMD ["python", "app.py"]
