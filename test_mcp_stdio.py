#!/usr/bin/env python3
"""
Test MCP STDIO server before connecting to Claude Desktop
"""

import subprocess
import json
import sys
import time

def test_mcp_stdio():
    """Test the MCP server with STDIO protocol"""
    print("🧪 Testing MCP STDIO Server")
    print("=" * 50)
    
    # Test message sequence
    messages = [
        {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {}
            },
            "id": 1
        },
        {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
    ]
    
    # Start the MCP server
    print("Starting MCP server...")
    proc = subprocess.Popen(
        [sys.executable, "mcp_local_bridge.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # Send initialize
        print("\n1. Sending initialize request...")
        msg = json.dumps(messages[0]) + "\n"
        proc.stdin.write(msg)
        proc.stdin.flush()
        
        # Read response
        response = proc.stdout.readline()
        if response:
            data = json.loads(response)
            if "result" in data:
                print("   ✅ Initialize successful")
                print(f"   Server: {data['result'].get('serverInfo', {}).get('name', 'Unknown')}")
            else:
                print(f"   ❌ Initialize failed: {data}")
                return False
        else:
            print("   ❌ No response from server")
            return False
        
        # Send tools/list
        print("\n2. Listing available tools...")
        msg = json.dumps(messages[1]) + "\n"
        proc.stdin.write(msg)
        proc.stdin.flush()
        
        # Read response
        response = proc.stdout.readline()
        if response:
            data = json.loads(response)
            if "result" in data and "tools" in data["result"]:
                tools = data["result"]["tools"]
                print(f"   ✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"      • {tool['name']} - {tool['description'][:50]}...")
                return True
            else:
                print(f"   ❌ Tools list failed: {data}")
                return False
        else:
            print("   ❌ No response for tools list")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        # Print stderr if available
        stderr = proc.stderr.read()
        if stderr:
            print(f"\nServer errors:\n{stderr}")
        return False
        
    finally:
        proc.terminate()
        proc.wait()

def check_prerequisites():
    """Check if prerequisites are met"""
    print("Checking prerequisites...")
    
    # Check if MCP is installed
    try:
        import mcp
        print("✅ MCP SDK installed")
    except ImportError:
        print("❌ MCP SDK not installed. Run: pip install mcp")
        return False
    
    # Check if services are running
    import requests
    try:
        requests.get("http://localhost:8080/health", timeout=2)
        print("✅ Catalog Manager running")
    except:
        print("❌ Catalog Manager not running on localhost:8080")
        return False
        
    try:
        requests.get("http://localhost:8081/health", timeout=2)
        print("✅ Fault Manager running")
    except:
        print("❌ Fault Manager not running on localhost:8081")
        return False
    
    return True

if __name__ == "__main__":
    print("MCP STDIO Server Test")
    print("=" * 50)
    
    if not check_prerequisites():
        print("\n⚠️  Fix the issues above before proceeding")
        sys.exit(1)
    
    print("\nTesting MCP server...")
    if test_mcp_stdio():
        print("\n✅ MCP server is working correctly!")
        print("\nNext steps:")
        print("1. Copy the Claude Desktop config:")
        print("   cp claude_desktop_config_local.json ~/Library/Application\\ Support/Claude/claude_desktop_config.json")
        print("2. Restart Claude Desktop")
        print("3. Look for 'telepath-fault-local' in Claude's MCP menu")
    else:
        print("\n❌ MCP server test failed")
        print("\nTroubleshooting:")
        print("1. Check if all services are running")
        print("2. Make sure you're in the correct directory")
        print("3. Check Python dependencies: pip install mcp aiohttp")
