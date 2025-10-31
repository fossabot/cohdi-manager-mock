FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt install -y vim && apt clean
RUN mkdir -p /app/certs

COPY certs/server.crt /app/certs
COPY certs/server.key /app/certs
COPY app.py .
COPY in /app/in
RUN mkdir -p /app/out

EXPOSE 443

CMD ["python", "app.py"]
