#!/usr/bin/env python3
"""
Test script for known connections functionality.
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
            print(f"  - {conn_id}: {conn['name']} ({conn['port']})")
        return data
    except Exception as e:
        print(f"Error listing connections: {e}")
        return None


def test_get_connection_details(connection_id):
    """Test getting details for a specific connection."""
    try:
        response = requests.get(f"{BASE_URL}/connections/{connection_id}")
        print(f"Get Connection '{connection_id}' Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Connection Details:")
            print(f"  Name: {data['name']}")
            print(f"  Description: {data['description']}")
            print(f"  Port: {data['port']}")
            print(f"  Device Type: {data['device_type']}")
            print(f"  Model: {data['model']}")
            print(f"  Location: {data['location']}")
            print(f"  Common Commands: {', '.join(data['common_commands'])}")
        return response.json()
    except Exception as e:
        print(f"Error getting connection details: {e}")
        return None


def test_connect_by_id(connection_id):
    """Test connecting using a known connection ID."""
    try:
        data = {"connection_id": connection_id}
        response = requests.post(
            f"{BASE_URL}/connect/by-id",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Connect by ID '{connection_id}' Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error connecting by ID: {e}")
        return None


def test_connect_default():
    """Test connecting to the default connection."""
    try:
        response = requests.post(f"{BASE_URL}/connect/default")
        print(f"Connect Default Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error connecting to default: {e}")
        return None


def test_connections_by_type(device_type):
    """Test listing connections by device type."""
    try:
        response = requests.get(f"{BASE_URL}/connections/by-type/{device_type}")
        print(f"Connections by Type '{device_type}' Status: {response.status_code}")
        data = response.json()
        print(f"Found {data['count']} connections of type '{device_type}':")
        for conn in data['connections']:
            print(f"  - {conn['id']}: {conn['name']}")
        return data
    except Exception as e:
        print(f"Error getting connections by type: {e}")
        return None


def test_enhanced_status():
    """Test the enhanced status endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/status")
        print(f"Status: {response.status_code}")
        print(f"Enhanced Status Response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"Error checking status: {e}")
        return None


def main():
    """Run all known connections tests."""
    print("=" * 60)
    print("Testing Known Connections Functionality")
    print("=" * 60)

    print("\n1. Listing all known connections...")
    connections_data = test_list_known_connections()

    if connections_data and connections_data['known_connections']:
        # Get the first connection ID for testing
        first_conn_id = list(connections_data['known_connections'].keys())[0]

        print(f"\n2. Getting details for '{first_conn_id}'...")
        test_get_connection_details(first_conn_id)

        print("\n3. Testing connection by device type...")
        test_connections_by_type("SEL_RELAY")

        print("\n4. Testing connection to default...")
        test_connect_default()

        print("\n5. Checking enhanced status...")
        test_enhanced_status()

        print("\n6. Testing connect by ID...")
        test_connect_by_id("test_device")

        print("\n7. Final status check...")
        test_enhanced_status()

    else:
        print("No known connections found or error occurred")

    print("\n" + "=" * 60)
    print("Known Connections Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("You can start it with:")
    print("uvicorn src.server.main:app --host 127.0.0.1 --port 8000 --reload")
    print()

    # Wait a moment for user to read
    time.sleep(2)
    main()
