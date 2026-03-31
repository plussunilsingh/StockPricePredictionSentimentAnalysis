# Slim Dockerfile for Hugging Face Spaces (prefer binary wheels)
# Uses Python 3.11 and avoids installing Rust/cargo to keep image small.
# If a package needs to be built from source, this image will fail; prefer
# packages/wheels that are available for manylinux and Python 3.11.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install a small set of system deps required by many wheels (but NOT cargo/rust)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libffi-dev \
       libssl-dev \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY requirements.txt /app/requirements.txt

# Upgrade pip and install requirements, prefer binary wheels to avoid source builds
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir uvicorn[standard] pydantic || true && \
    pip install --no-cache-dir --prefer-binary -r /app/requirements.txt

# Copy project files
COPY . /app

# Add healthcheck script and make executable
COPY healthcheck.sh /app/healthcheck.sh
RUN chmod +x /app/healthcheck.sh

# Healthcheck: run the healthcheck script; give services plenty of time to start
HEALTHCHECK --interval=10s --timeout=5s --start-period=180s --retries=20 CMD /app/healthcheck.sh || exit 1

# EXPOSE 8000 8005 (Disabled for generic PaaS like Railway, which relies on PORT env var)

# Use the same entrypoint script (it will create a .venv inside container)
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["start"]
