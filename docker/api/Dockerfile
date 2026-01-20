# Use the official Python image.
FROM python:3.8-slim

# Set the working directory in the container.
WORKDIR /usr/src/app

# Install dependencies.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install system packages.
RUN apt-get update \
    && apt-get install -y \
    libgl1 \ 
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application.
COPY . .

# Command to run the application.
CMD ["python", "app.py"]
