FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps — git untuk pip install git+..., curl untuk healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy metadata dulu (layer cache)
COPY pyproject.toml README.md LICENSE ./
COPY dorker ./dorker

# Install editable + dev deps
RUN pip install --upgrade pip && pip install -e ".[dev]"

# Non-root user (security)
RUN useradd -m -u 1000 bugdork \
    && mkdir -p /home/bugdork/.config/bugdork \
    && chown -R bugdork:bugdork /app /home/bugdork/.config
USER bugdork

# Default: run test
CMD ["pytest", "-v"]
