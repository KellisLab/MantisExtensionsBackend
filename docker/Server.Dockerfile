FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git

RUN rm -rf /var/lib/apt/lists/*

COPY . .
RUN python -m pip install --no-cache-dir -r ./src/requirements.txt

EXPOSE 8111