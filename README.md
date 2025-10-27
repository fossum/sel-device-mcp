# sel-device-mcp

An MCP (Model Context Protocol) server to allow AI intelligent access to Schweitzer Engineering Laboratories (SEL) devices. Utilizes telnet and serial communication protocols to interact with connected devices through a REST API interface.

## Features

- **Serial Communication**: Full support for COM port connections (default: COM5)
- **REST API Interface**: FastAPI-based server with comprehensive endpoints
- **SEL Device Support**: Pre-configured for SEL device prompts and protocols
- **Real-time Connection Management**: Connect, disconnect, and monitor device status
- **Command Execution**: Send commands to connected devices with configurable timeouts
- **Comprehensive Error Handling**: Detailed error responses and logging
- **Interactive API Documentation**: Swagger UI for testing and exploration
- **Type-safe Implementation**: Pydantic models for request validation

## API Endpoints

- `POST /connect` - Connect to a serial device (default: COM5, 9600 baud)
- `POST /disconnect` - Disconnect from the current device
- `POST /command` - Send commands to connected device
- `GET /status` - Check current connection status
- `GET /` - Server health check
- `GET /docs` - Interactive API documentation

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)
- Access to SEL device via serial port or telnet

### Installation

1. Clone the repository:

```bash
git clone https://github.com/fossum/sel-device-mcp.git
cd sel-device-mcp
```

1. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

1. Install dependencies:

```bash
pip install -r requirements.txt
# OR using pipenv
pipenv install
```

### Quick Start

1. **Start the MCP server:**

```bash
# Option 1: Direct start
python src/server/main.py

# Option 2: Using uvicorn
uvicorn src.server.main:app --host 127.0.0.1 --port 8000 --reload

# Option 3: Using the batch file
start_server.bat

# Option 4: Using pipenv
pipenv run uvicorn src.server.main:app --host 127.0.0.1 --port 8000 --reload
```

1. **Access the API:**
   - Server: `http://localhost:8000`
   - Interactive docs: `http://localhost:8000/docs`

1. **Connect to COM5:**

```bash
# Default connection (COM5, 9600 baud, 10s timeout)
curl -X POST "http://localhost:8000/connect"

# Custom connection parameters
curl -X POST "http://localhost:8000/connect" \
     -H "Content-Type: application/json" \
     -d '{"port": "COM5", "baudrate": 9600, "timeout": 10.0}'
```

1. **Send commands:**

```bash
curl -X POST "http://localhost:8000/command" \
     -H "Content-Type: application/json" \
     -d '{"command": "ID", "timeout": 5.0}'
```

1. **Check connection status:**

```bash
curl -X GET "http://localhost:8000/status"
```

## Usage Examples

### Python Client Example

```python
import requests

# Connect to device
response = requests.post("http://localhost:8000/connect", json={
    "port": "COM5",
    "baudrate": 9600,
    "timeout": 10.0
})
print(f"Connection: {response.json()}")

# Send command
response = requests.post("http://localhost:8000/command", json={
    "command": "ID",
    "timeout": 5.0
})
print(f"Response: {response.json()}")

# Check status
response = requests.get("http://localhost:8000/status")
print(f"Status: {response.json()}")

# Disconnect
response = requests.post("http://localhost:8000/disconnect")
print(f"Disconnect: {response.json()}")
```

### PowerShell Example

```powershell
# Connect to device
$response = Invoke-RestMethod -Uri "http://localhost:8000/connect" -Method POST -ContentType "application/json" -Body '{"port": "COM5", "baudrate": 9600}'

# Send command
$response = Invoke-RestMethod -Uri "http://localhost:8000/command" -Method POST -ContentType "application/json" -Body '{"command": "ID"}'

# Check status
$response = Invoke-RestMethod -Uri "http://localhost:8000/status" -Method GET
```

## Project Structure

```
sel-device-mcp/
├── src/
│   ├── core/
│   │   └── mcp.py              # Core MCP functionality
│   ├── device/
│   │   ├── connector.py        # Abstract connector interface
│   │   ├── serial_connector.py # Serial communication implementation
│   │   └── telnet_connector.py # Telnet communication implementation
│   └── server/
│       ├── main.py            # FastAPI application
│       └── routes.py          # API endpoints
├── tests/
│   └── test_main.py           # Unit tests
├── requirements.txt           # Python dependencies
├── Pipfile                   # Pipenv configuration
├── start_server.bat         # Windows startup script
└── README.md               # This file
```

## Configuration

### Connection Parameters

- **port**: Serial port name (default: "COM5")
- **baudrate**: Communication speed (default: 9600)
- **timeout**: Connection timeout in seconds (default: 10.0)

## Error Handling

The API provides detailed error responses:

- **400 Bad Request**: Connection failures, invalid parameters
- **408 Request Timeout**: Command timeouts
- **500 Internal Server Error**: Unexpected errors

All errors include descriptive messages for troubleshooting.

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

The project follows PEP 8 standards with 79-character line limits.

## Troubleshooting

### Common Issues

1. **"No module named 'fastapi'"**: Run `pip install -r requirements.txt`
2. **"Permission denied" on COM port**: Ensure no other application is using the port
3. **Connection timeout**: Check device connection and port settings
4. **Port not found**: Verify the correct COM port number in Device Manager

### Logging

The server provides detailed logging for debugging connection and command issues.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Write tests for new functionality
4. Ensure code follows PEP 8 standards
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
