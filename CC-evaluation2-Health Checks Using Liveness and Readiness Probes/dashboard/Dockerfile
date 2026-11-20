# ---- Monitoring dashboard image (Flask, port 8080) ----
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .
COPY static ./static
EXPOSE 8080
CMD ["python", "server.py"]
