#!/bin/bash
# Run tests inside a Docker container

echo "Running tests in Docker container..."

docker run --rm \
  --network mcp_cm_v1_telecom_network \
  -v $(pwd):/app \
  -w /app \
  python:3.11-slim \
  bash -c "pip install -q aiohttp && python test_mcp.py"
