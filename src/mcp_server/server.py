"""
MCP Server implementation for SEL device communication.
This implements the Model Context Protocol for use with AI assistants.
Enhanced with device capabilities and AFT integration.
"""

import json
import logging
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    CallToolResult,
    ListResourcesResult,
    ListToolsResult,
    ReadResourceResult,
)

from ..core.connection_manager import connection_manager
from ..core.connection_factory import ConnectionFactory
from ..device.connector import ConnectionError


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection state
current_connection = None


def load_device_capabilities() -> Dict[str, Any]:
    """Load device capabilities from YAML configuration file."""
    try:
        capabilities_file = Path(__file__).parent.parent.parent / "config" / "device_capabilities.yaml"
        with open(capabilities_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.warning(f"Could not load device capabilities: {e}")
        return {"device_capabilities": {}, "aft_capabilities": {}}


# Load capabilities at startup
CAPABILITIES = load_device_capabilities()
DEVICE_CAPABILITIES = CAPABILITIES.get("device_capabilities", {})
AFT_CAPABILITIES = CAPABILITIES.get("aft_capabilities", {})

# Create MCP server
server = Server("sel-device-mcp")


def get_device_capabilities(model: str) -> Optional[Dict[str, Any]]:
    """Get capabilities for a specific device model."""
    return DEVICE_CAPABILITIES.get(model)


def validate_command_for_device(command: str, model: str) -> Dict[str, Any]:
    """Validate if a command is appropriate for a device model."""
    capabilities = get_device_capabilities(model)
    if not capabilities:
        return {
            "validated": False,
            "reason": f"No capabilities found for {model}"
        }

    command_base = command.split()[0].upper()
    is_known = command_base in capabilities.get("commands", [])

    return {
        "validated": True,
        "is_known_command": is_known,
        "device_model": model,
        "command_base": command_base
    }


@server.list_resources()
async def list_resources() -> ListResourcesResult:
    """List available resources including device capabilities."""
    resources = []

    # Add known connections as resources
    for conn_id, conn in connection_manager.get_known_connections().items():
        resources.append(
            Resource(
                uri=f"connection://{conn_id}",
                name=f"Device: {conn.name}",
                description=conn.description,
                mimeType="application/json"
            )
        )

    # Add device capabilities as resources
    for model in DEVICE_CAPABILITIES.keys():
        resources.append(
            Resource(
                uri=f"device-capabilities://{model}",
                name=f"{model} Capabilities",
                description=f"Commands, access levels, and capabilities for {model}",
                mimeType="application/json"
            )
        )

    # Add AFT capabilities
    resources.append(
        Resource(
            uri="aft://capabilities",
            name="AFT Testing Capabilities",
            description="Available AFT (Automated Functional Testing) capabilities",
            mimeType="application/json"
        )
    )

    # Add current connection status
    resources.append(
        Resource(
            uri="status://current",
            name="Current Connection Status",
            description="Status of the currently active connection",
            mimeType="application/json"
        )
    )

    return ListResourcesResult(resources=resources)


@server.read_resource()
async def read_resource(uri: str) -> ReadResourceResult:
    """Read a specific resource."""

    if uri.startswith("connection://"):
        # Return connection details with device capabilities
        conn_id = uri.replace("connection://", "")
        conn = connection_manager.get_connection(conn_id)

        if not conn:
            raise ValueError(f"Connection '{conn_id}' not found")

        # Enhance with device capabilities if available
        conn_data = conn.to_dict()
        if conn.model in DEVICE_CAPABILITIES:
            conn_data["device_capabilities"] = DEVICE_CAPABILITIES[conn.model]

        content = TextContent(
            type="text",
            text=json.dumps(conn_data, indent=2)
        )
        return ReadResourceResult(contents=[content])

    elif uri.startswith("device-capabilities://"):
        # Return device capabilities
        model = uri.replace("device-capabilities://", "")
        if model not in DEVICE_CAPABILITIES:
            raise ValueError(f"No capabilities found for device model: {model}")

        content = TextContent(
            type="text",
            text=json.dumps(DEVICE_CAPABILITIES[model], indent=2)
        )
        return ReadResourceResult(contents=[content])

    elif uri == "aft://capabilities":
        # Return AFT capabilities
        content = TextContent(
            type="text",
            text=json.dumps(AFT_CAPABILITIES, indent=2)
        )
        return ReadResourceResult(contents=[content])

    elif uri == "status://current":
        # Return current connection status
        global current_connection

        if current_connection:
            if hasattr(current_connection, 'host'):  # Telnet
                status = {
                    "connected": True,
                    "connection_type": "telnet",
                    "host": current_connection.host,
                    "port": current_connection.port,
                    "timeout": current_connection.timeout
                }
            else:  # Serial
                status = {
                    "connected": True,
                    "connection_type": "serial",
                    "port": current_connection.port,
                    "baudrate": current_connection.baudrate,
                    "timeout": current_connection.timeout
                }

            # Add device capabilities if available
            if hasattr(current_connection, '_known_conn') and current_connection._known_conn:
                model = current_connection._known_conn.model
                if model in DEVICE_CAPABILITIES:
                    status["device_capabilities"] = DEVICE_CAPABILITIES[model]
        else:
            status = {
                "connected": False,
                "message": "No active connection"
            }

        content = TextContent(
            type="text",
            text=json.dumps(status, indent=2)
        )
        return ReadResourceResult(contents=[content])

    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools."""
    tools = [
        Tool(
            name="list_connections",
            description="List all known device connections",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="connect_device",
            description="Connect to a device using connection ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "connection_id": {
                        "type": "string",
                        "description": "ID of the known connection to use"
                    },
                    "override_host": {
                        "type": "string",
                        "description": "Override host for telnet connections"
                    },
                    "override_port": {
                        "type": "string",
                        "description": "Override port for serial connections"
                    },
                    "override_baudrate": {
                        "type": "integer",
                        "description": "Override baudrate for serial"
                    },
                    "override_timeout": {
                        "type": "number",
                        "description": "Override timeout for any connection"
                    }
                },
                "required": ["connection_id"]
            }
        ),
        Tool(
            name="disconnect_device",
            description="Disconnect from the currently connected device",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="send_command",
            description="Send a command to the connected device",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to send to the device"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Timeout for command execution",
                        "default": 10.0
                    }
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="get_connection_status",
            description="Get the current connection status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_device_capabilities",
            description="Get capabilities and features for a device model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Device model (e.g., SEL-411L)"
                    }
                },
                "required": ["model"]
            }
        ),
        Tool(
            name="authenticate_device",
            description="Authenticate to device with access level",
            inputSchema={
                "type": "object",
                "properties": {
                    "level": {
                        "type": "string",
                        "description": "Access level (1, 2, 3, etc.)",
                        "default": "1"
                    },
                    "password": {
                        "type": "string",
                        "description": "Password for the access level"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="check_aft_availability",
            description="Check if AFT (Automated Testing) available",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

    return ListToolsResult(tools=tools)


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    global current_connection

    try:
        if name == "list_connections":
            connections = connection_manager.get_known_connections()
            result = {
                "connections": {},
                "count": len(connections)
            }

            for conn_id, conn in connections.items():
                conn_info = conn.to_dict()

                # Add device capabilities summary if available
                if conn.model in DEVICE_CAPABILITIES:
                    caps = DEVICE_CAPABILITIES[conn.model]
                    conn_info["capabilities"] = {
                        "command_count": len(caps['commands']),
                        "supports_aft": caps.get('supports_aft', False),
                        "supports_ip_config": caps.get(
                            'supports_ip_config',
                            False
                        ),
                        "access_levels": list(
                            caps.get('access_levels', {}).keys()
                        )
                    }

                result["connections"][conn_id] = conn_info

            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            )

        elif name == "connect_device":
            connection_id = arguments["connection_id"]

            # Get the known connection
            known_conn = connection_manager.get_connection(connection_id)
            if not known_conn:
                raise ValueError(f"Connection '{connection_id}' not found")

            # Disconnect existing connection if any
            if current_connection:
                current_connection.disconnect()

            # Create connection using factory
            current_connection = ConnectionFactory.create_connector(
                known_conn=known_conn,
                override_host=arguments.get("override_host"),
                override_port=arguments.get("override_port"),
                override_baudrate=arguments.get("override_baudrate"),
                override_timeout=arguments.get("override_timeout")
            )

            # Connect
            current_connection.connect()

            # Store reference to known connection for device capabilities
            current_connection._known_conn = known_conn

            result = {
                "status": "connected",
                "connection_id": connection_id,
                "connection_name": known_conn.name,
                "description": known_conn.description,
                "connection_type": known_conn.connection_type,
                "device_type": known_conn.device_type,
                "model": known_conn.model,
                "location": known_conn.location
            }

            # Add device capabilities if available
            if known_conn.model in DEVICE_CAPABILITIES:
                caps = DEVICE_CAPABILITIES[known_conn.model]
                result["device_capabilities"] = {
                    "command_count": len(caps['commands']),
                    "supports_aft": caps.get('supports_aft', False),
                    "supports_ip_config": caps.get('supports_ip_config', False),
                    "access_levels": list(caps.get('access_levels', {}).keys())
                }

            logger.info(f"Connected to {known_conn.name}")

            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            )

        elif name == "disconnect_device":
            if not current_connection:
                result = {
                    "status": "no_connection",
                    "message": "No active connection"
                }
            else:
                connection_info = getattr(
                    current_connection,
                    'port',
                    f"{current_connection.host}:{current_connection.port}"
                )
                current_connection.disconnect()
                current_connection = None
                result = {
                    "status": "disconnected",
                    "message": f"Disconnected from {connection_info}"
                }
                logger.info(f"Disconnected from {connection_info}")

            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            )

        elif name == "send_command":
            if not current_connection:
                raise ConnectionError(
                    "No active connection. Please connect first."
                )

            command = arguments["command"]
            timeout = arguments.get("timeout", 10.0)

            # Validate command if we have device capabilities
            if hasattr(current_connection, '_known_conn'):
                conn = current_connection._known_conn
                validation_result = validate_command_for_device(
                    command,
                    conn.model
                )
                if not validation_result["validated"]:
                    logger.warning(
                        "Command validation warning: "
                        + str(validation_result['reason'])
                    )

            response = current_connection.send_command(command, timeout)

            result = {
                "status": "success",
                "command": command,
                "response": response,
                "timeout": timeout
            }

            logger.info(f"Command '{command}' executed successfully")

            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            )

        elif name == "get_connection_status":
            if current_connection:
                if hasattr(current_connection, 'host'):  # Telnet
                    result = {
                        "connected": True,
                        "connection_type": "telnet",
                        "host": current_connection.host,
                        "port": current_connection.port,
                        "timeout": current_connection.timeout
                    }
                else:  # Serial
                    result = {
                        "connected": True,
                        "connection_type": "serial",
                        "port": current_connection.port,
                        "baudrate": current_connection.baudrate,
                        "timeout": current_connection.timeout
                    }

                # Add device capabilities if available
                if hasattr(current_connection, '_known_conn'):
                    conn = current_connection._known_conn
                    result.update({
                        "device_name": conn.name,
                        "device_model": conn.model
                    })
                    if conn.model in DEVICE_CAPABILITIES:
                        caps = DEVICE_CAPABILITIES[conn.model]
                        result["device_capabilities"] = {
                            "command_count": len(caps['commands']),
                            "supports_aft": caps.get('supports_aft', False),
                            "supports_ip_config": caps.get(
                                'supports_ip_config',
                                False
                            )
                        }
            else:
                result = {
                    "connected": False,
                    "message": "No active connection",
                    "available_connections": len(
                        connection_manager.get_known_connections()
                    )
                }

            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            )

        elif name == "get_device_capabilities":
            model = arguments.get("model")
            if not model:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="Error: model parameter is required"
                    )]
                )

            capabilities = get_device_capabilities(model)
            if not capabilities:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"No capabilities found for device model: {model}"
                    )]
                )

            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(capabilities, indent=2)
                )]
            )

        elif name == "authenticate_device":
            level = arguments.get("level", "1")
            password = arguments.get("password")

            if not current_connection:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="Error: No active connection"
                    )]
                )

            try:
                # Check if device supports authentication levels
                if hasattr(current_connection, '_known_conn'):
                    conn = current_connection._known_conn
                    if conn.model in DEVICE_CAPABILITIES:
                        caps = DEVICE_CAPABILITIES[conn.model]
                        supported_levels = caps.get('access_levels', {})
                        if level not in supported_levels:
                            return CallToolResult(
                                content=[TextContent(
                                    type="text",
                                    text=(
                                        f"Warning: Level {level} not in known "
                                        f"levels for {conn.model}"
                                    )
                                )]
                            )

                # Send authentication command
                if password:
                    command = f"ACC {level} {password}"
                else:
                    command = f"ACC {level}"

                response = current_connection.send_command(command, 5)
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Authentication result: {response}"
                    )]
                )

            except Exception as e:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Authentication failed: {str(e)}"
                    )]
                )

        elif name == "check_aft_availability":
            try:
                # Try to import AFT modules
                import sel.aft_shared.ams
                import sel.aft_shared.common.testing
            except ImportError as e:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"AFT modules not available: {str(e)}"
                    )]
                )

            # Check if we have an active connection with AFT support
            aft_supported = False
            device_info = None

            if (
                current_connection and
                hasattr(current_connection, '_known_conn')
            ):
                conn = current_connection._known_conn
                if conn.model in DEVICE_CAPABILITIES:
                    caps = DEVICE_CAPABILITIES[conn.model]
                    aft_supported = caps.get('supports_aft', False)
                    device_info = {
                        "model": conn.model,
                        "name": conn.name,
                        "aft_supported": aft_supported
                    }

            result = {
                "aft_modules_available": True,
                "ams_class_available": hasattr(sel.aft_shared.ams, 'AMS'),
                "testing_available": True,
                "current_device": device_info,
                "aft_capabilities": AFT_CAPABILITIES
            }

            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            )
        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool call failed: {e}")
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": str(e),
                    "tool": name
                }, indent=2)
            )],
            isError=True
        )


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sel-device-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
