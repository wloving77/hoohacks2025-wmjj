# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy entire project into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Set environment variable (optional but recommended)
ENV FLASK_APP=app.py

# Start the Flask server
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
