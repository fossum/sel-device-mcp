# Enhancing MCP with SEL Device and AFT Insights

This guide explains how to provide the MCP with deeper insights into SEL devices and AFT (Automated Functional Testing) capabilities, making it more intelligent and helpful when working with SEL equipment.

## Overview

The enhanced MCP server provides additional intelligence about:

1. **SEL Device Capabilities** - Commands, access levels, and features per device model
2. **AFT Integration** - Access to Automated Functional Testing capabilities
3. **Device-Specific Operations** - Model-aware command validation and suggestions
4. **Testing Automation** - Integration with AMS (Automated Test Management System)

## Enhanced MCP Server

### Configuration

The enhanced server is available alongside the standard server:

```json
{
  "servers": {
    "sel-mcp-device-server": {
      "command": "C:/development/ericfoss/sel-device-mcp/.venv/Scripts/python.exe",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "c:\\development\\ericfoss\\sel-device-mcp"
    },
    "sel-mcp-device-server-enhanced": {
      "command": "C:/development/ericfoss/sel-device-mcp/.venv/Scripts/python.exe",
      "args": ["-m", "src.mcp_server.enhanced_server"],
      "cwd": "c:\\development\\ericfoss\\sel-device-mcp"
    }
  }
}
```

### New Capabilities

#### 1. Device Capabilities Knowledge Base

The enhanced server includes a comprehensive knowledge base of SEL device capabilities:

```python
SEL_DEVICE_CAPABILITIES = {
    "SEL-411L": {
        "type": "Line Current Differential Relay",
        "common_commands": ["ID", "ACC", "2ACCESS", "STATUS", "METER", ...],
        "access_levels": {
            "0": "No access",
            "1": "Monitor relay functions",
            "2": "Full control",
            "A": "Automation commands",
            "B": "Monitor and control circuit breakers"
        },
        "ip_configuration": {
            "supported": True,
            "commands": ["SET IP", "SET SUBNET", "SET GATEWAY", "SET DHCP"]
        },
        "testing_capabilities": ["Protection testing", "Current differential"]
    }
}
```

#### 2. AFT Integration

Access to AFT (Automated Functional Testing) capabilities through the `sel.aft_shared` modules:

- **AMS (Automated Test Management System)** functions
- **Test execution and control**
- **I/O monitoring and control**
- **Test file management**

#### 3. Enhanced Tools

##### Device Intelligence Tools

- **`get_device_capabilities`** - Get model-specific capabilities and commands
- **`authenticate_device`** - Smart authentication with access level awareness
- **`discover_device_info`** - Comprehensive device discovery and diagnostics

##### AFT Integration Tools

- **`check_aft_availability`** - Verify AFT package availability and capabilities
- **`get_ams_status`** - Get detailed AMS capabilities and methods

##### Enhanced Existing Tools

- **`list_connections`** - Now includes device capabilities for each connection
- **`send_command`** - Validates commands against device capabilities
- **`get_connection_status`** - Includes device-specific information

## Usage Examples

### With GitHub Copilot

The enhanced MCP provides much richer context to AI assistants:

```plaintext
"What commands are available on the SEL-411L?"
"Connect to the SEL-411L and authenticate to Level 2"
"Check if AFT testing capabilities are available"
"Discover all information about the connected device"
"What access levels does the SEL-2411 support?"
"Send the STATUS command and validate it's appropriate for this device"
```

### Direct Tool Usage

#### Get Device Capabilities
```json
{
  "tool": "get_device_capabilities",
  "arguments": {
    "model": "SEL-411L"
  }
}
```

Response includes:
- Device type and description
- Available commands
- Access levels and their meanings
- IP configuration support
- Testing capabilities

#### Check AFT Availability
```json
{
  "tool": "check_aft_availability",
  "arguments": {}
}
```

Response includes:
- AFT package availability
- Available AMS functions
- Supported test types

#### Enhanced Device Connection
```json
{
  "tool": "connect_device",
  "arguments": {
    "connection_id": "sel_411l_1"
  }
}
```

Response now includes:
- Standard connection information
- Device capabilities for the connected model
- Available commands and access levels

## AFT Integration Details

### Available AMS Functions

The enhanced server provides access to these AMS capabilities:

- **Test Execution**
  - `execute_test_wait_for_finish` - Run test and wait for completion
  - `execute_test_return` - Start test and return immediately
  - `abort_running_test` - Stop currently running test

- **Test Management**
  - `send_new_test_file_xmodem` - Upload new test files
  - `perform_self_test` - Run AMS self-diagnostics
  - `get_firmware_revision` - Get AMS firmware information

- **I/O Control**
  - `get_input_states` - Read all input contact states
  - `close_output_contact` - Control output contacts
  - `open_output_contacts` - Control output contacts
  - `set_analog_output_voltage` - Set analog output levels

### Using AFT with SEL Devices

1. **Check AFT Availability**
   ```plaintext
   "Check if AFT testing capabilities are available"
   ```

2. **Get AMS Status**
   ```plaintext
   "Show me the AMS status and available methods"
   ```

3. **Device + AFT Integration**
   ```plaintext
   "Connect to SEL-411L and check if it can be used with AFT testing"
   ```

## Device-Specific Intelligence

### Command Validation

The enhanced server validates commands against device capabilities:

```python
# When sending "METER" command
{
  "validation": {
    "command_validated": True,
    "is_known_command": True,  # METER is in SEL-411L common commands
    "device_model": "SEL-411L"
  }
}
```

### Access Level Awareness

Smart authentication based on device capabilities:

```python
# SEL-411L supports these access levels
"access_levels": {
  "0": "No access",
  "1": "Monitor relay functions",
  "2": "Full control",
  "A": "Automation commands",
  "B": "Monitor and control circuit breakers",
  "O": "Output",
  "P": "Protection"
}
```

### IP Configuration Support

Automatic detection of IP configuration capabilities:

```python
# SEL-411L supports IP configuration
"ip_configuration": {
  "supported": True,
  "commands": ["SET IP", "SET SUBNET", "SET GATEWAY", "SET DHCP"]
}

# SEL-421 is serial-only
"ip_configuration": {
  "supported": False,
  "note": "Serial connection device"
}
```

## Resources

### Device Capabilities Resources

Access device capabilities as MCP resources:

- `device-capabilities://SEL-411L` - SEL-411L capabilities
- `device-capabilities://SEL-2411` - SEL-2411 capabilities
- `device-capabilities://SEL-421` - SEL-421 capabilities

### AFT Resources

- `aft://capabilities` - AFT testing capabilities and supported test types

### Enhanced Connection Resources

- `connection://sel_411l_1` - Now includes device capabilities
- `status://current` - Enhanced with device-specific information

## Benefits for AI Assistants

The enhanced MCP provides AI assistants with:

1. **Context-Aware Responses** - Knows what commands work with which devices
2. **Validation and Safety** - Prevents invalid commands from being sent
3. **Intelligent Suggestions** - Can suggest appropriate commands for specific tasks
4. **Testing Integration** - Understands both manual device control and automated testing
5. **Comprehensive Discovery** - Can fully characterize unknown devices

## Migration from Basic MCP

To switch from the basic to enhanced MCP server:

1. **Update VS Code Configuration**
   ```json
   "sel-mcp-device-server-enhanced": {
     "command": "C:/development/ericfoss/sel-device-mcp/.venv/Scripts/python.exe",
     "args": ["-m", "src.mcp_server.enhanced_server"],
     "cwd": "c:\\development\\ericfoss\\sel-device-mcp"
   }
   ```

2. **Restart VS Code** to load the enhanced server

3. **Test Enhanced Capabilities**
   ```plaintext
   "What capabilities does the SEL-411L have?"
   "Check AFT availability"
   "Connect to SEL-411L and show its capabilities"
   ```

## Extending the Knowledge Base

### Adding New Device Models

Add new devices to `SEL_DEVICE_CAPABILITIES`:

```python
"SEL-NEW-MODEL": {
    "type": "Device Type Description",
    "common_commands": ["ID", "STATUS", ...],
    "access_levels": {
        "1": "Description",
        "2": "Description"
    },
    "ip_configuration": {
        "supported": True/False,
        "commands": ["SET IP", ...]
    },
    "testing_capabilities": ["Test type 1", "Test type 2"]
}
```

### Adding AFT Capabilities

Extend `AFT_CAPABILITIES` with new test types or AMS functions:

```python
AFT_CAPABILITIES = {
    "ams_functions": [...],
    "supported_test_types": [...],
    "new_capability": "description"
}
```

## Troubleshooting

### AFT Import Issues

If AFT modules aren't available:

1. **Check Package Installation**
   ```bash
   pip list | grep aft
   ```

2. **Verify Import Path**
   ```python
   from sel.aft_shared.ams import AMS  # Correct import
   ```

3. **Check AFT Availability Tool**
   ```plaintext
   "Check if AFT testing capabilities are available"
   ```

### Device Capability Issues

If device capabilities aren't showing:

1. **Verify Device Model** in `known_connections.json`
2. **Check Model Name** matches exactly in `SEL_DEVICE_CAPABILITIES`
3. **Add Missing Models** to the knowledge base

## Related Documentation

- [MCP Server Guide](MCP%20Server%20Guide.md) - Basic MCP setup
- [VS Code Integration Guide](VS%20Code%20Integration%20Guide.md) - VS Code configuration
- [AFT Documentation] - External AFT package documentation
- Device Manuals - SEL device command references
