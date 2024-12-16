# Base Image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy source code
COPY src/ ./src/
COPY requirements.txt ./
COPY .env ./

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Run the Flask app
CMD ["python", "src/main.py"]
