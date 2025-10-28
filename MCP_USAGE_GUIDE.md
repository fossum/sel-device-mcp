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
pip install -r requirements.txt
```

### 2. Configure VS Code for MCP

You need to add the MCP server configuration to your VS Code settings. There are two ways to do this:

#### Option A: User Settings (Recommended)

1. Open VS Code Command Palette (`Ctrl+Shift+P`)
2. Type "Preferences: Open User Settings (JSON)"
3. Add this configuration to your `settings.json`:

```json
{
  "github.copilot.chat.experimental.mcp.servers": {
    "sel-device-mcp": {
      "command": "python",
      "args": ["c:/development/ericfoss/sel-device-mcp/start_mcp_server.py"],
      "env": {
        "PYTHONPATH": "c:/development/ericfoss/sel-device-mcp/src"
      }
    }
  }
}
```

#### Option B: Workspace Settings

1. Create `.vscode/settings.json` in your project root
2. Add the same configuration as above

### 3. Restart VS Code

After adding the configuration, restart VS Code to load the MCP server.

## Verifying the Setup

1. Open GitHub Copilot Chat in VS Code
2. The MCP server should automatically start when you begin a chat session
3. You can verify it's working by asking Copilot about SEL devices

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

```
"Show me all available SEL device connections"

"Connect to the SEL 2411 device and check its status"

"Send the command 'STATUS' to the connected device"

"What's the current connection status?"

"Disconnect from the device"
```

## Known Device Connections

The system comes pre-configured with these devices:

- **SEL 2411 Relay** (Telnet connection to 192.168.1.100:23)
- **SEL 421 Relay** (Serial connection to COM5)

You can modify these in `config/known_connections.json`.

## Troubleshooting

### MCP Server Not Starting
1. Check that Python is in your PATH
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Check VS Code Developer Console (`Help > Toggle Developer Tools`) for errors

### Connection Issues
1. Verify device IP addresses and ports in `config/known_connections.json`
2. Check that serial ports are available and not in use
3. Ensure network connectivity for telnet connections

### GitHub Copilot Not Recognizing MCP
1. Ensure you have the latest GitHub Copilot extension
2. Verify the MCP configuration is correctly added to settings.json
3. Restart VS Code after making configuration changes

## Advanced Configuration

### Custom Device Connections

To add new devices, edit `config/known_connections.json`:

```json
{
  "my_device": {
    "name": "My SEL Device",
    "description": "Custom SEL device configuration",
    "connection_type": "serial",
    "device_type": "SEL",
    "model": "SEL-XXX",
    "location": "Building A",
    "port": "COM3",
    "baudrate": 9600,
    "timeout": 5.0
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

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in VS Code Developer Console
3. Verify device connectivity outside of the MCP system
