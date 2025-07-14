#!/usr/bin/env python3
"""
Test if fault_manager.py can run locally
"""

import subprocess
import time
import requests
import sys
import os

def test_fault_manager():
    """Test fault manager locally"""
    print("Testing Fault Manager locally...")
    
    # Check if dependencies are installed
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ Dependencies found")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nInstall with: pip install -r requirements_fault.txt")
        return False
    
    # Start fault manager in subprocess
    print("\nStarting fault manager on port 8082 (test port)...")
    env = os.environ.copy()
    env['PORT'] = '8082'
    
    proc = subprocess.Popen(
        [sys.executable, 'fault_manager.py'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for startup
    print("Waiting for startup...")
    time.sleep(5)
    
    # Check if it's running
    try:
        response = requests.get('http://localhost:8082/health')
        if response.status_code == 200:
            print("✅ Fault manager started successfully!")
            print(f"   Response: {response.json()}")
            
            # Test fault check endpoint
            fault_response = requests.post(
                'http://localhost:8082/serviceStatus/check',
                json={"location": {"streetName": "Main Street", "city": "Dublin"}}
            )
            if fault_response.status_code == 200:
                print("✅ Fault simulation is working!")
                data = fault_response.json()
                print(f"   Status: {data.get('status')}")
                if data.get('networkFaults'):
                    print(f"   Fault: {data['networkFaults'][0]['description']}")
            
            success = True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            success = False
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        success = False
    
    # Clean up
    proc.terminate()
    proc.wait()
    
    return success

if __name__ == "__main__":
    print("Fault Manager Local Test")
    print("=" * 40)
    
    if test_fault_manager():
        print("\n✅ Fault manager works locally!")
        print("\nThe issue might be with Docker configuration.")
        print("Try running: ./fix_fault_manager.sh")
    else:
        print("\n❌ Fault manager has issues.")
        print("\nCheck the error messages above.")
