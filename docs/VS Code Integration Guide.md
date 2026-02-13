# SEL Device Communication Guide for VS Code

## Quick Start

1. Add the server to the .vscode/mcp.json file.

```json
{
    "servers": {
        "sel-mcp-device-server": {
            "command": "C:/development/ericfoss/sel-device-mcp/.venv/Scripts/python.exe",
            "args": ["-m", "src.mcp_server.server"],
            "cwd": "c:\\development\\ericfoss\\sel-device-mcp"
        }
    },
    "inputs": []
}
```

1. Start the mcp server.

## Example Usage with GitHub Copilot

You can ask GitHub Copilot to help you with device communication:

**Example prompts:**

- "Help me connect to a SEL device using curl"
- "Show me how to send commands to the connected device"
- "Create a Python script to automate device communication"
- "How do I connect to my SEL device and get its status?"
- "Write a script to automate sending multiple commands to a SEL device"
- "Help me parse the response from my device communication API"

## Known Device Configurations

Devices are configured on the server side with the known_configuration.json.

## Troubleshooting

- Commands timeout: Increase timeout values or check device responsiveness
