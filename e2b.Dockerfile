# E2B Custom Template for PostHog Driver
#
# This Dockerfile creates an E2B sandbox template with all dependencies pre-installed.
#
# Build: e2b template build
# Use:   Sandbox.create("your-template-id")
#
# Benefits:
# - PostHog driver pre-installed
# - Mock PostHog API ready to run
# - All dependencies installed (requests, fastapi, uvicorn, duckdb)
# - Sandbox starts in ~150ms (no installation time!)

FROM python:3.11-slim

# Set working directory
WORKDIR /home/user

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy driver files
COPY base_driver.py .
COPY posthog_driver.py .

# Copy mock API
COPY mock_posthog_api/ ./mock_posthog_api/

# Copy recipes (for Claude Agent SDK)
COPY driver_recipes.py .

# Install Python dependencies
RUN pip install --no-cache-dir \
    requests>=2.31.0 \
    fastapi>=0.104.0 \
    uvicorn>=0.24.0 \
    duckdb>=0.9.0

# Pre-warm mock API database (creates tables on first import)
RUN python3 -c "import sys; sys.path.insert(0, '/home/user/mock_posthog_api'); import db, fixtures; db.init_db(); fixtures.load_fixtures()"

# Verify installation
RUN python3 -c "from base_driver import BaseAPIDriver; from posthog_driver import PostHogDriver; print('✓ PostHog driver imported successfully')"

# Set Python path
ENV PYTHONPATH=/home/user:$PYTHONPATH

# Template metadata
LABEL maintainer="your-email@example.com"
LABEL description="E2B template for PostHog data extraction driver"
LABEL version="1.0.0"
