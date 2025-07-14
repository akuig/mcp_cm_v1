#!/usr/bin/env python3
"""
Local MCP bridge for Claude Desktop - runs on host machine
Connects to Docker services running on localhost
"""

import os
import sys

# Set environment variables for local services
os.environ["CATALOG_MANAGER_URL"] = "http://localhost:8080"
os.environ["FAULT_MANAGER_URL"] = "http://localhost:8081"

# Import and run the stdio server
from mcp_stdio_server_fault import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
