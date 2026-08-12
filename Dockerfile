# Use official Python 3.11 lightweight slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Run seed database script on startup if DB not present
RUN python seed.py

# Expose backend port
EXPOSE 5000

# Start Uvicorn multi-worker server
CMD ["uvicorn", "main:combined_app", "--host", "0.0.0.0", "--port", "5000", "--workers", "4"]
