# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Install dependencies for Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    --no-install-recommends

# Install Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set display port to avoid crash
ENV DISPLAY=:99

# Set search directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables for headless mode
ENV HEADLESS=1

# Run the application with gunicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
