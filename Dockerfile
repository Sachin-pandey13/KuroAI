# KuroAI v1.0 RC-2 — Multi-Stage Dockerfile
# Supports CPU and GPU execution modes.

# ────────────────────────────────────────────────────────────
# Stage 1: Dependency builder
# ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements-lock.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements-lock.txt

# ────────────────────────────────────────────────────────────
# Stage 2: Runtime image
# ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL maintainer="KuroAI Team"
LABEL version="1.0.0-rc2"
LABEL description="KuroAI Generative AI Pipeline"

# Create non-root user for security
RUN groupadd -r kuroai && useradd -r -g kuroai kuroai

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY backend/ ./backend/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY exceptions.py ./
COPY .env.example ./.env.example

# Ensure outputs directory exists
RUN mkdir -p /app/outputs /app/data && \
    chown -R kuroai:kuroai /app

USER kuroai

# Expose API port
EXPOSE 8000

# Default: start the FastAPI health/metrics server
CMD ["uvicorn", "backend.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
