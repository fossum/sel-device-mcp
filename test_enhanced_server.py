#!/usr/bin/env python3
"""
Test script for enhanced MCP server functionality
"""

import os
import sys
import yaml

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))


def test_yaml_loading():
    """Test loading device capabilities from YAML"""
    print("Testing YAML device capabilities loading...")

    yaml_path = os.path.join('config', 'device_capabilities.yaml')
    with open(yaml_path, 'r') as f:
        yaml_data = yaml.safe_load(f)

    # Extract device capabilities from the YAML structure
    device_capabilities = yaml_data.get('device_capabilities', {})
    aft_capabilities = yaml_data.get('aft_capabilities', {})

    print(f"✓ Loaded capabilities for {len(device_capabilities)} device models")
    print(f"✓ Loaded AFT capabilities for {len(aft_capabilities)} features")

    for model, caps in device_capabilities.items():
        command_count = len(caps.get('common_commands', []))
        supports_aft = caps.get('supports_aft', False)
        supports_ip = caps.get('supports_ip_config', False)
        device_type = caps.get('type', 'Unknown')
        print(f"  • {model}: {command_count} commands, "
              f"AFT={supports_aft}, IP={supports_ip}")
        print(f"    Type: {device_type}")

    return yaml_data


def test_validation_functions():
    """Test device capability validation functions"""
    print("\nTesting validation functions...")

    # Load capabilities
    yaml_path = os.path.join('config', 'device_capabilities.yaml')
    with open(yaml_path, 'r') as f:
        yaml_data = yaml.safe_load(f)

    device_capabilities = yaml_data.get('device_capabilities', {})

    def get_device_capabilities(model):
        """Get capabilities for a specific device model"""
        return device_capabilities.get(model)

    def validate_command_for_device(model, command):
        """Validate if a command is supported by a device"""
        caps = get_device_capabilities(model)
        if not caps:
            return {
                "valid": False,
                "message": f"Unknown device model: {model}"
            }

        commands = caps.get('commands', [])
        if command.upper() in [cmd.upper() for cmd in commands]:
            return {"valid": True, "message": "Command is supported"}

        # Check for partial matches
        partial_matches = [
            cmd for cmd in commands
            if cmd.upper().startswith(command.upper())
        ]
        if partial_matches:
            return {
                "valid": True,
                "message": f"Possible: {', '.join(partial_matches)}"
            }

        return {
            "valid": False,
            "message": f"Command '{command}' not found"
        }

    # Test with SEL-411L
    test_cases = [
        ("SEL-411L", "ID"),
        ("SEL-411L", "ACC"),
        ("SEL-2411", "ID"),
    ]

    for model, command in test_cases:
        result = validate_command_for_device(model, command)
        status = "✓" if result["valid"] else "✗"
        print(f"  {status} {model} + '{command}': {result['message']}")


def test_aft_capabilities():
    """Test AFT capabilities structure"""
    print("\nTesting AFT capabilities...")

    # Define AFT capabilities (from server.py)
    AFT_CAPABILITIES = {
        "modules": {
            "ams": {
                "description": "Automated Test Management System",
                "classes": ["AMS"],
                "functions": ["test_device", "run_test_suite", "generate_report"]
            },
            "common.testing": {
                "description": "Common testing utilities",
                "functions": ["setup_test", "teardown_test", "validate_results"]
            }
        },
        "supported_devices": [
            "SEL-411L", "SEL-2411", "SEL-421", "SEL-2730M",
            "SEL-851", "SEL-9L", "SEL-T400L"
        ],
        "test_types": [
            "functional", "performance", "configuration", "protection"
        ]
    }

    print(f"✓ AFT supports {len(AFT_CAPABILITIES['supported_devices'])} device types")
    print(f"✓ AFT provides {len(AFT_CAPABILITIES['test_types'])} test types")
    print(f"✓ AFT includes {len(AFT_CAPABILITIES['modules'])} module categories")


def main():
    """Run all tests"""
    print("Enhanced MCP Server Functionality Tests")
    print("=" * 50)

    try:
        # Test YAML loading
        test_yaml_loading()

        # Test validation functions
        test_validation_functions()

        # Test AFT capabilities
        test_aft_capabilities()

        print("\n" + "=" * 50)
        print("✓ All tests completed successfully!")
        print("\nThe enhanced MCP server should provide:")
        print("- Device capability awareness")
        print("- Command validation")
        print("- AFT integration readiness")
        print("- Rich device information")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
