#!/usr/bin/env python3
"""
Test script for COM5 connection functionality.
"""

import requests
import json
import time

# Server URL
BASE_URL = "http://localhost:8000"

def test_connection_status():
    """Check current connection status."""
    try:
        response = requests.get(f"{BASE_URL}/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error checking status: {e}")
        return None

def test_connect_to_com5():
    """Test connecting to COM5."""
    try:
        # Default connection to COM5
        response = requests.post(f"{BASE_URL}/connect")
        print(f"Connect Status: {response.status_code}")
        print(f"Connect Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error connecting: {e}")
        return None

def test_connect_with_custom_settings():
    """Test connecting to COM5 with custom settings."""
    try:
        data = {
            "port": "COM5",
            "baudrate": 9600,
            "timeout": 2.0
        }
        response = requests.post(
            f"{BASE_URL}/connect",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Custom Connect Status: {response.status_code}")
        print(f"Custom Connect Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error connecting with custom settings: {e}")
        return None

def test_send_command():
    """Test sending a command to the connected device."""
    try:
        data = {
            "command": "STATUS",
            "timeout": 5.0
        }
        response = requests.post(
            f"{BASE_URL}/command",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Command Status: {response.status_code}")
        print(f"Command Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error sending command: {e}")
        return None

def test_disconnect():
    """Test disconnecting from the device."""
    try:
        response = requests.post(f"{BASE_URL}/disconnect")
        print(f"Disconnect Status: {response.status_code}")
        print(f"Disconnect Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error disconnecting: {e}")
        return None

def main():
    """Run all tests."""
    print("=" * 50)
    print("Testing COM5 Connection Functionality")
    print("=" * 50)

    print("\n1. Checking initial status...")
    test_connection_status()

    print("\n2. Testing default connection to COM5...")
    test_connect_to_com5()

    print("\n3. Checking status after connection...")
    test_connection_status()

    print("\n4. Testing command sending...")
    test_send_command()

    print("\n5. Testing disconnection...")
    test_disconnect()

    print("\n6. Checking final status...")
    test_connection_status()

    print("\n" + "=" * 50)
    print("Test complete!")
    print("=" * 50)

if __name__ == "__main__":
    print("Make sure the FastAPI server is running on http://localhost:8002")
    print("You can start it with:")
    print("uvicorn src.server.main:app --host 127.0.0.1 --port 8002 --reload")
    print()

    # Wait a moment for user to read
    time.sleep(2)
    main()
