# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port that Cloud Run expects
EXPOSE 8080

# Start the FastAPI server
CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8080"]
