# Use the official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port that the Flask app runs on
EXPOSE 5000

# Use Gunicorn for serving the app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "hfsa_app:create_app()"]


