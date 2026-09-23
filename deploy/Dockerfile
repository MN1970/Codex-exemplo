FROM python:3.11-slim

LABEL maintainer="mneves@mantaassociados.com"
LABEL description="Maestro APScheduler v5.0 - Background tasks orchestrator"
LABEL version="5.0"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    jq \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create maestro user
RUN useradd -m -u 1000 maestro

# Set working directory
WORKDIR /opt/maestro

# Copy application code
COPY --chown=maestro:maestro . /opt/maestro/

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir \
    schedule==1.2.0 \
    requests==2.31.0 \
    prometheus-client==0.19.0 \
    python-dotenv==1.0.0 \
    pydantic==2.5.0

# Create log directory
RUN mkdir -p /var/log/maestro && chown -R maestro:maestro /var/log/maestro

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose metrics port
EXPOSE 8080

# Switch to maestro user
USER maestro

# Run scheduler
CMD ["python3", "/opt/maestro/scripts/apscheduler_setup.py"]
