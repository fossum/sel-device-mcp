"""
MCP Server implementation for SEL device communication.
This implements the Model Context Protocol for use with AI assistants.
"""

import json
import logging
from typing import Any, Dict

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

# Create MCP server
server = Server("sel-device-mcp")


@server.list_resources()
async def list_resources() -> ListResourcesResult:
    """List available resources (known connections)."""
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
        # Return connection details
        conn_id = uri.replace("connection://", "")
        conn = connection_manager.get_connection(conn_id)

        if not conn:
            raise ValueError(f"Connection '{conn_id}' not found")

        content = TextContent(
            type="text",
            text=json.dumps(conn.to_dict(), indent=2)
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
                "connections": {
                    conn_id: conn.to_dict()
                    for conn_id, conn in connections.items()
                },
                "count": len(connections)
            }

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

            logger.info(f"Connected to {known_conn.name}")

            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            )

        elif name == "disconnect_device":
            if not current_connection:
                result = {"status": "no_connection", "message": "No active connection"}
            else:
                connection_info = getattr(current_connection, 'port',
                                        f"{current_connection.host}:{current_connection.port}")
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
                raise ConnectionError("No active connection. Please connect first.")

            command = arguments["command"]
            timeout = arguments.get("timeout", 10.0)

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
            else:
                result = {
                    "connected": False,
                    "message": "No active connection",
                    "available_connections": len(connection_manager.get_known_connections())
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
