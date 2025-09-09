# Atlas Remote MCP for CapRover
# Production-ready Docker image with multi-stage build
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    HOST=0.0.0.0 \
    PORT=80

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user that matches common host UIDs
# Using UID 1000 which is typical for the first non-root user
RUN groupadd -g 1000 auto && \
    useradd -u 1000 -g auto -m -s /bin/bash auto

# Copy Python packages from builder and adjust ownership
COPY --from=builder --chown=auto:auto /root/.local /home/auto/.local
ENV PATH=/home/auto/.local/bin:$PATH

# Set working directory
WORKDIR /app

# Copy application code with proper ownership
COPY --chown=auto:auto src/ ./src/
COPY --chown=auto:auto run_server.py ./

# Create data directories with proper permissions
RUN mkdir -p /data/shared /data/user /data/projects /data/workspace /mcp/projects && \
    chown -R auto:auto /data /mcp /app && \
    chmod -R 775 /data /mcp

# Switch to non-root user
USER auto

# Health check for CapRover
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Expose port 80 for CapRover
EXPOSE 80

# Run the server as non-root user
CMD ["python", "run_server.py"]
