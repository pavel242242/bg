# Multi-stage Dockerfile for HuggingFace Spaces (Docker SDK).
# Spaces routes HTTPS traffic to port 7860 inside the container.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy \
    HF_HOME=/app/.cache/huggingface

# uv = fast pip; copy a pre-built static binary instead of pulling cargo.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# HF Spaces runs as user 1000 by default — create matching home + cache dirs.
RUN useradd -m -u 1000 user && mkdir -p /app /app/.cache/huggingface && chown -R user:user /app
USER user
WORKDIR /app

# Install Python deps first for layer caching.
COPY --chown=user:user pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy source + data.
COPY --chown=user:user backend/ ./backend/
COPY --chown=user:user frontend/ ./frontend/
COPY --chown=user:user data/ ./data/

EXPOSE 7860
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
