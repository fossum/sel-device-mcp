# sel-device-mcp

An MCP (Model Context Protocol) server to allow AI intelligent access to Schweitzer Engineering Laboratories (SEL) devices. Utilizes telnet and serial communication protocols to interact with connected devices.

## Features

- Serial and Telnet device connectivity
- Prompt detection and response handling
- Configurable timeouts and connection parameters
- FastAPI-based MCP server
- Comprehensive logging
- Type-safe implementations

## Getting Started

### Prerequisites

- Python 3.11 or higher
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
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

### Usage

1. Start the MCP server:

```bash
python src/server/main.py
```

1. Connect to a device:

```python
from src.device.serial_connector import SerialConnector
from src.core.mcp import MCP

# For Serial connection
connector = SerialConnector('/dev/ttyUSB0', baudrate=9600)
mcp = MCP(connector)

try:
    mcp.connect()
    response = mcp.send_command('ACCESS LEVEL VIEW')
    print(response)
finally:
    mcp.disconnect()
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
