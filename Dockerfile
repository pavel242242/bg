# Use official Apify Python image
FROM apify/actor-python:3.11

# Copy requirements first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src ./src

# Set the main module
ENV APIFY_MAIN_FILE=src/main.py

# Run the actor
CMD python3 -m apify
