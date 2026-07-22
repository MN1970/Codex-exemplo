FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run as non-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Verify installation
RUN python -c "import cag.shadow_mode; print('✓ CAG Shadow Mode ready')"

# Default command (can be overridden)
CMD ["python", "-m", "pytest", "cag/tests/", "-v"]
