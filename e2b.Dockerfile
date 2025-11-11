# E2B Custom Template for Grafana & PostHog Drivers
#
# This Dockerfile creates an E2B sandbox template with all dependencies pre-installed.
#
# Build: e2b template build
# Use:   Sandbox.create("your-template-id")
#
# Benefits:
# - All drivers pre-installed
# - All mock APIs ready to run
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
COPY grafana_driver.py .
COPY posthog_driver.py .

# Copy mock APIs
COPY mock_grafana_api/ ./mock_grafana_api/
COPY mock_posthog_api/ ./mock_posthog_api/

# Copy templates (needed for agent executor)
COPY script_templates.py .

# Install Python dependencies
RUN pip install --no-cache-dir \
    requests>=2.31.0 \
    fastapi>=0.104.0 \
    uvicorn>=0.24.0 \
    duckdb>=0.9.0

# Optional: Pre-warm mock API database
# (Creates tables on first import)
RUN python3 -c "import sys; sys.path.insert(0, '/home/user/mock_grafana_api'); import db, fixtures; db.init_db(); fixtures.load_fixtures()"
RUN python3 -c "import sys; sys.path.insert(0, '/home/user/mock_posthog_api'); import db, fixtures; db.init_db(); fixtures.load_fixtures()"

# Verify installation
RUN python3 -c "from base_driver import BaseAPIDriver; from grafana_driver import GrafanaDriver; from posthog_driver import PostHogDriver; print('✓ All drivers imported successfully')"

# Set Python path
ENV PYTHONPATH=/home/user:$PYTHONPATH

# Template metadata (optional)
LABEL maintainer="your-email@example.com"
LABEL description="E2B template for Grafana & PostHog data extraction drivers"
LABEL version="1.0.0"
