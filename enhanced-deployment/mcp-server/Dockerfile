FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY mcp_server_working_copy.py .

# Create logs directory
RUN mkdir -p /app/logs

# Health check - just check if port is open, not specific endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD nc -z localhost 8090 || exit 1

# Expose port
EXPOSE 8090

# Run the exact copy of working FastMCP approach
CMD ["python", "mcp_server_working_copy.py"]
