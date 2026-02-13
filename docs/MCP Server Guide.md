# Using SEL Device MCP in VS Code

This guide explains how to set up and use the SEL Device MCP (Model Context Protocol) server with GitHub Copilot in VS Code.

## Prerequisites

1. **Python Environment**: Ensure you have Python 3.8+ installed
2. **VS Code**: Latest version with GitHub Copilot extension
3. **Dependencies**: Install required Python packages

## Installation Steps

### 1. Install Python Dependencies

```powershell
cd c:\development\ericfoss\sel-device-mcp
python -m venv .venv
.venv/bin/activate
pip install -r requirements.txt
```

## Available MCP Tools

Once configured, GitHub Copilot can use these tools to interact with SEL devices:

### Connection Management

- **`list_connections`**: View all configured device connections
- **`connect_device`**: Connect to a specific device by ID
- **`disconnect_device`**: Disconnect from current device
- **`get_connection_status`**: Check current connection status

### Device Communication

- **`send_command`**: Send commands to connected devices

### Resources

- **Device Configurations**: Access known device profiles
- **Connection Status**: Real-time connection information

## Example Usage

Here are some example prompts you can use with GitHub Copilot:

```plaintext
"Show me all available SEL device connections"

"Connect to the SEL 2411 device and check its status"

"Send the command 'STATUS' to the connected device"

"What's the current connection status?"

"Can you ask the SEL-411l what commands it has?"

"Disconnect from the device"
```

## Known Device Connections

The system comes pre-configured with these devices:

### Telnet Connections (AFT Test Devices)

- **SEL 2411** - Programmable automation controller (10.39.86.231:23)
- **SEL 2730M** - Managed 24-port ethernet switch (10.39.86.233:23) - Eric's Rack
- **SEL 411L** - Line current differential relay (10.39.86.234:23) - Eric's Rack
- **SEL 851** - Feeder protection relay (10.39.86.233:23)
- **SEL 9L** - Line relay (10.39.86.215:23) - Austin's Rack
- **SEL T400L** - Transformer relay (10.39.86.235:23) - Eric's Rack

### Serial Connections

- **SEL 421** - Protection, automation, and control system (COM5, 9600 baud) - Eric's Rack

You can modify these in `config/known_connections.json`.

## Troubleshooting

### MCP Server Not Starting

1. Check that Python is in your PATH
1. Verify all dependencies are installed: `pip install -r requirements.txt`
1. Check VS Code Developer Console (`Help > Toggle Developer Tools`) for errors
1. Review logs in VS Code Developer Console

### Connection Issues

1. Verify device IP addresses and ports in `config/known_connections.json`
1. Check that serial ports are available and not in use
1. Ensure network connectivity for telnet connections

### GitHub Copilot Not Recognizing MCP

For detailed VS Code setup and troubleshooting, see the
[VS Code Integration Guide](VS%20Code%20Integration%20Guide.md).

## Advanced Configuration

### Custom Device Connections

To add new devices, edit `config/known_connections.json`:

**Serial Device Example:**

```json
{
  "my_serial_device": {
    "name": "My SEL Device",
    "description": "Custom SEL device configuration",
    "connection_type": "serial",
    "device_type": "SEL_RELAY",
    "model": "SEL-XXX",
    "location": "Building A",
    "port": "COM3",
    "baudrate": 9600,
    "timeout": 5.0,
    "common_commands": ["ID", "STATUS", "ACC", "QUIT"]
  }
}
```

**Telnet Device Example:**

```json
{
  "my_telnet_device": {
    "name": "My Remote SEL Device",
    "description": "Custom telnet SEL device configuration",
    "connection_type": "telnet",
    "device_type": "SEL_RELAY",
    "model": "SEL-XXX",
    "location": "Remote Site",
    "host": "192.168.1.100",
    "telnet_port": 23,
    "timeout": 10.0,
    "common_commands": ["ID", "STATUS", "ACC", "QUIT"]
  }
}
```

### Environment Variables

You can set these environment variables for additional configuration:

- `SEL_MCP_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `SEL_MCP_CONFIG_PATH`: Custom path to known_connections.json

## API Documentation

The MCP server also provides a REST API that runs alongside the MCP protocol. This is useful for testing and debugging:

- **Base URL**: `http://localhost:8000` (when REST server is running)
- **Swagger Docs**: `http://localhost:8000/docs`

### REST Endpoints

- `POST /connect/by-id/{connection_id}`: Connect to device
- `POST /command`: Send command to connected device
- `GET /status`: Get connection status
- `GET /connections`: List known connections
- `DELETE /disconnect`: Disconnect from device

## Security Considerations

- The MCP server runs locally and communicates with devices on your network
- Serial connections require appropriate permissions
- Network connections should use secure, trusted devices only
- Consider firewall rules for telnet connections
