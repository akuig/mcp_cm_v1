#!/usr/bin/env python3
"""
Test the stdio MCP server
"""

import subprocess
import json
import time

def test_stdio_server():
    # Start the stdio server
    proc = subprocess.Popen(
        ['python3', 'mcp_stdio_server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    time.sleep(1)
    
    try:
        # Test 1: Initialize
        print("Testing initialize...")
        request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0"
                }
            },
            "id": 1
        }
        
        proc.stdin.write(json.dumps(request) + '\n')
        proc.stdin.flush()
        
        response = proc.stdout.readline()
        print(f"Response: {response}")
        
        # Test 2: List tools
        print("\nTesting tools/list...")
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        proc.stdin.write(json.dumps(request) + '\n')
        proc.stdin.flush()
        
        response = proc.stdout.readline()
        print(f"Response: {response}")
        
        # Test 3: Send notification
        print("\nTesting notification...")
        request = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        proc.stdin.write(json.dumps(request) + '\n')
        proc.stdin.flush()
        
        # No response expected for notifications
        time.sleep(0.5)
        
        print("All tests completed!")
        
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    # Make sure the HTTP server is running first
    print("Make sure the HTTP MCP server is running (make up)")
    print("Testing stdio server...\n")
    test_stdio_server()
