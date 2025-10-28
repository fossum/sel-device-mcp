#!/usr/bin/env python3
"""
Test script for updated known connections with telnet support.
"""

import requests
import json
import time

# Server URL
BASE_URL = "http://localhost:8000"


def test_list_known_connections():
    """Test listing all known connections."""
    try:
        response = requests.get(f"{BASE_URL}/connections")
        print(f"List Connections Status: {response.status_code}")
        data = response.json()
        print(f"Found {data['count']} known connections:")
        for conn_id, conn in data['known_connections'].items():
            conn_type = conn.get('connection_type', 'unknown')
            if conn_type == 'telnet':
                endpoint = f"{conn.get('host')}:{conn.get('telnet_port')}"
            else:
                endpoint = conn.get('port', 'unknown')
            print(f"  - {conn_id}: {conn['name']} ({conn_type}: {endpoint})")
        return data
    except Exception as e:
        print(f"Error listing connections: {e}")
        return None


def test_connect_telnet_by_id():
    """Test connecting to telnet device by ID."""
    try:
        data = {"connection_id": "sel_relay_lab"}
        response = requests.post(
            f"{BASE_URL}/connect/by-id",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Connect Telnet by ID Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error connecting by ID: {e}")
        return None


def test_connect_serial_by_id():
    """Test connecting to serial device by ID."""
    try:
        data = {"connection_id": "sel_meter_field"}
        response = requests.post(
            f"{BASE_URL}/connect/by-id",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Connect Serial by ID Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error connecting by ID: {e}")
        return None


def test_direct_telnet_connect():
    """Test direct telnet connection."""
    try:
        data = {
            "host": "10.39.86.231",
            "port": 23,
            "timeout": 10.0
        }
        response = requests.post(
            f"{BASE_URL}/connect/telnet",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Direct Telnet Connect Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error with direct telnet connect: {e}")
        return None


def test_send_command():
    """Test sending a command."""
    try:
        data = {
            "command": "ID",
            "timeout": 5.0
        }
        response = requests.post(
            f"{BASE_URL}/command",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Command Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error sending command: {e}")
        return None


def test_enhanced_status():
    """Test the enhanced status endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/status")
        print(f"Status: {response.status_code}")
        print("Enhanced Status Response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"Error checking status: {e}")
        return None


def test_disconnect():
    """Test disconnection."""
    try:
        response = requests.post(f"{BASE_URL}/disconnect")
        print(f"Disconnect Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error disconnecting: {e}")
        return None


def main():
    """Run all tests for telnet and serial support."""
    print("=" * 60)
    print("Testing Known Connections with Telnet Support")
    print("=" * 60)

    print("\n1. Listing all known connections...")
    connections_data = test_list_known_connections()

    if connections_data and connections_data['known_connections']:

        print("\n2. Testing direct telnet connection...")
        test_direct_telnet_connect()

        print("\n3. Checking status after telnet connection...")
        test_enhanced_status()

        print("\n4. Testing telnet command...")
        test_send_command()

        print("\n5. Disconnecting from telnet...")
        test_disconnect()

        print("\n6. Testing connection by ID (telnet)...")
        test_connect_telnet_by_id()

        print("\n7. Checking status after telnet by ID...")
        test_enhanced_status()

        print("\n8. Disconnecting...")
        test_disconnect()

        print("\n9. Testing connection by ID (serial)...")
        test_connect_serial_by_id()

        print("\n10. Checking status after serial by ID...")
        test_enhanced_status()

        print("\n11. Final disconnect...")
        test_disconnect()

    else:
        print("No known connections found or error occurred")

    print("\n" + "=" * 60)
    print("Telnet and Serial Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("You can start it with:")
    print("uvicorn src.server.main:app --host 127.0.0.1 --port 8000 --reload")
    print()

    # Wait a moment for user to read
    time.sleep(2)
    main()
