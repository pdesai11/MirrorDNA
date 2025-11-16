# Multi-stage build for MirrorDNA

# Stage 1: Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY setup.py README.md ./
COPY src/ ./src/
COPY schemas/ ./schemas/

# Install Python dependencies
RUN pip install --no-cache-dir --user -e .

# Stage 2: Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Create data directories
RUN mkdir -p /data/.mirrordna/data /data/.mirrordna/logs /data/.mirrordna/keys

# Set environment variables
ENV MIRRORDNA_DATA_DIR=/data/.mirrordna/data
ENV MIRRORDNA_LOG_DIR=/data/.mirrordna/logs
ENV PYTHONUNBUFFERED=1

# Expose port for API server (if enabled)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD mirrordna health || exit 1

# Default command
ENTRYPOINT ["mirrordna"]
CMD ["--help"]
