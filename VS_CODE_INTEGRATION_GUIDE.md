# SEL Device Communication Guide for VS Code

## Quick Start

1. **Start the Server:**

   ```powershell
   cd c:\development\ericfoss\sel-device-mcp
   pipenv run uvicorn src.server.main:app --host 127.0.0.1 --port 8000
   ```

1. **Access API Documentation:**

   Open http://localhost:8000/docs in your browser

## Available Endpoints

- `GET /connections` - List all known device connections
- `POST /connect/by-id/{connection_id}` - Connect to a device
- `POST /command` - Send command to connected device
- `GET /status` - Check connection status
- `DELETE /disconnect` - Disconnect from device

## Example Usage with GitHub Copilot

You can ask GitHub Copilot to help you with device communication:

**Example prompts:**

- "Help me connect to a SEL device using curl"
- "Show me how to send commands to the connected device"
- "Create a Python script to automate device communication"

**Sample Commands:**

```powershell
# List available connections
curl -X GET "http://localhost:8000/connections"

# Connect to SEL 2411 device
curl -X POST "http://localhost:8000/connect/by-id/sel_2411"

# Send a command
curl -X POST "http://localhost:8000/command" -H "Content-Type: application/json" -d '{"command": "ID", "timeout": 10.0}'

# Check status
curl -X GET "http://localhost:8000/status"

# Disconnect
curl -X DELETE "http://localhost:8000/disconnect"
```

## VS Code Integration

### 1. REST Client Extension

Install the "REST Client" extension in VS Code and create `.http` files:

```http
### List Connections
GET http://localhost:8000/connections

### Connect to Device
POST http://localhost:8000/connect/by-id/sel_2411

### Send Command
POST http://localhost:8000/command
Content-Type: application/json

{
  "command": "ID",
  "timeout": 10.0
}

### Get Status
GET http://localhost:8000/status

### Disconnect
DELETE http://localhost:8000/disconnect
```

### 2. PowerShell Integration

Create a PowerShell script for common operations:

```powershell
# sel-device-helper.ps1
$BaseUrl = "http://localhost:8000"

function Get-SELConnections {
    Invoke-RestMethod -Uri "$BaseUrl/connections" -Method Get
}

function Connect-SELDevice {
    param([string]$DeviceId)
    Invoke-RestMethod -Uri "$BaseUrl/connect/by-id/$DeviceId" -Method Post
}

function Send-SELCommand {
    param([string]$Command, [float]$Timeout = 10.0)
    $body = @{ command = $Command; timeout = $Timeout } | ConvertTo-Json
    Invoke-RestMethod -Uri "$BaseUrl/command" -Method Post -Body $body -ContentType "application/json"
}

function Get-SELStatus {
    Invoke-RestMethod -Uri "$BaseUrl/status" -Method Get
}

function Disconnect-SELDevice {
    Invoke-RestMethod -Uri "$BaseUrl/disconnect" -Method Delete
}
```

### 3. GitHub Copilot Chat Usage

With the server running, ask GitHub Copilot:

- "How do I connect to my SEL device and get its status?"
- "Write a script to automate sending multiple commands to a SEL device"
- "Help me parse the response from my device communication API"

## Known Device Configurations

Your system is pre-configured with:

1. **SEL 2411 Relay**
   - Connection ID: `sel_2411`
   - Type: Telnet (192.168.1.100:23)

1. **SEL 421 Relay**
   - Connection ID: `sel_421`
   - Type: Serial (COM5, 9600 baud)

## Troubleshooting

1. **Server won't start**: Check that no other process is using port 8000
1. **Connection fails**: Verify device IP addresses and COM ports
1. **Commands timeout**: Increase timeout values or check device responsiveness

## Advanced Usage

For advanced automation, you can:

1. Create Python scripts that use the requests library
1. Build PowerShell workflows for device management
1. Use the API in conjunction with other VS Code extensions
1. Set up automated testing of device configurations
