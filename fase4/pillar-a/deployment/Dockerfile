# Multi-stage build for PAL service
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

LABEL maintainer="Manta Associados"
LABEL description="Platform Abstraction Layer for multi-platform git operations"

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL="INFO"

# Copy application code
COPY config_schema.yaml .
COPY platform_abstraction_layer.py .
COPY drivers/ ./drivers/
COPY detection/ ./detection/

# Create non-root user
RUN useradd -m -u 1000 pal && chown -R pal:pal /app
USER pal

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from platform_abstraction_layer import get_pal; pal = get_pal(); import asyncio; health = asyncio.run(pal.health_check()); exit(0 if health.get('overall_status') == 'healthy' else 1)" || exit 1

# Default command - can be overridden
CMD ["python", "-m", "pytest", "tests/", "-v"]
