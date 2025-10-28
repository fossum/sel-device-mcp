#!/usr/bin/env python3
"""
Test script for the connection factory pattern.
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.connection_manager import KnownConnection
from core.connection_factory import ConnectionFactory


def test_factory_with_telnet_connection():
    """Test factory with a telnet connection."""
    print("Testing Telnet Connection Factory...")

    # Create a mock telnet connection
    telnet_conn = KnownConnection(
        id="test_telnet",
        name="Test Telnet Device",
        description="A test telnet device",
        device_type="TEST",
        model="Virtual",
        location="Test Lab",
        common_commands=["ID", "STATUS"],
        timeout=10.0,
        host="10.39.86.231",
        telnet_port=23
    )

    print(f"Connection type detected: {telnet_conn.connection_type}")

    try:
        # Use factory to create connector
        connector = ConnectionFactory.create_connector(telnet_conn)
        print(f"Created connector: {type(connector).__name__}")
        print(f"Host: {connector.host}, Port: {connector.port}")
        print("✅ Telnet factory test passed!")
        return True
    except Exception as e:
        print(f"❌ Telnet factory test failed: {e}")
        return False


def test_factory_with_serial_connection():
    """Test factory with a serial connection."""
    print("\nTesting Serial Connection Factory...")

    # Create a mock serial connection
    serial_conn = KnownConnection(
        id="test_serial",
        name="Test Serial Device",
        description="A test serial device",
        device_type="TEST",
        model="Virtual",
        location="Test Lab",
        common_commands=["ID", "STATUS"],
        timeout=15.0,
        port="COM5",
        baudrate=9600,
        prompts=[">", "=>"]
    )

    print(f"Connection type detected: {serial_conn.connection_type}")

    try:
        # Use factory to create connector
        connector = ConnectionFactory.create_connector(serial_conn)
        print(f"Created connector: {type(connector).__name__}")
        print(f"Port: {connector.port}, Baudrate: {connector.baudrate}")
        print(f"Prompts: {connector.prompts}")
        print("✅ Serial factory test passed!")
        return True
    except Exception as e:
        print(f"❌ Serial factory test failed: {e}")
        return False


def test_factory_with_overrides():
    """Test factory with override parameters."""
    print("\nTesting Factory with Overrides...")

    # Create a base connection
    base_conn = KnownConnection(
        id="test_override",
        name="Test Override Device",
        description="A test device for overrides",
        device_type="TEST",
        model="Virtual",
        location="Test Lab",
        common_commands=["ID"],
        timeout=10.0,
        host="10.0.0.1",
        telnet_port=23
    )

    try:
        # Use factory with overrides
        connector = ConnectionFactory.create_connector(
            base_conn,
            override_host="192.168.1.100",
            override_telnet_port=2323,
            override_timeout=5.0
        )
        print(f"Original: {base_conn.host}:{base_conn.telnet_port}")
        print(f"Override: {connector.host}:{connector.port}")
        print(f"Timeout: {connector.timeout}")
        print("✅ Override test passed!")
        return True
    except Exception as e:
        print(f"❌ Override test failed: {e}")
        return False


def test_factory_direct_params():
    """Test factory with direct parameters."""
    print("\nTesting Factory with Direct Parameters...")

    try:
        # Create telnet connector directly
        telnet_conn = ConnectionFactory.create_connector_from_params(
            connection_type="telnet",
            host="example.com",
            port=23,
            timeout=8.0
        )
        print(f"Telnet: {telnet_conn.host}:{telnet_conn.port}")

        # Create serial connector directly
        serial_conn = ConnectionFactory.create_connector_from_params(
            connection_type="serial",
            port="COM3",
            baudrate=19200,
            timeout=12.0
        )
        print(f"Serial: {serial_conn.port} @ {serial_conn.baudrate}")
        print("✅ Direct parameters test passed!")
        return True
    except Exception as e:
        print(f"❌ Direct parameters test failed: {e}")
        return False


def test_factory_error_handling():
    """Test factory error handling."""
    print("\nTesting Factory Error Handling...")

    # Test with missing required fields
    try:
        invalid_conn = KnownConnection(
            id="invalid",
            name="Invalid",
            description="Missing required fields",
            device_type="TEST",
            model="Virtual",
            location="Test Lab",
            common_commands=[],
            timeout=10.0
            # Missing host/port for telnet and port/baudrate for serial
        )

        connector = ConnectionFactory.create_connector(invalid_conn)
        print("❌ Should have failed with missing fields")
        return False
    except ValueError as e:
        print(f"✅ Correctly caught error: {e}")
        return True
    except Exception as e:
        print(f"❌ Wrong exception type: {e}")
        return False


def main():
    """Run all factory tests."""
    print("=" * 50)
    print("Connection Factory Pattern Tests")
    print("=" * 50)

    tests = [
        test_factory_with_telnet_connection,
        test_factory_with_serial_connection,
        test_factory_with_overrides,
        test_factory_direct_params,
        test_factory_error_handling
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1

    print(f"\n" + "=" * 50)
    print(f"Factory Tests Complete: {passed}/{len(tests)} passed")
    print("=" * 50)

    if passed == len(tests):
        print("🎉 All factory tests passed!")
    else:
        print("⚠️  Some factory tests failed")


if __name__ == "__main__":
    main()
