
import logging
from typing import Optional, Union

from fastapi import APIRouter, HTTPException

from pydantic import BaseModel

from ..device.serial_connector import SerialConnector
from ..device.telnet_connector import TelnetConnector
from ..device.connector import ConnectionError, TimeoutError
from ..core.connection_manager import connection_manager
from ..core.connection_factory import ConnectionFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Global connection manager
current_connection: Optional[Union[SerialConnector, TelnetConnector]] = None


class SerialConnectRequest(BaseModel):
    port: str = "COM5"
    baudrate: int = 9600
    timeout: float = 10


class TelnetConnectRequest(BaseModel):
    host: str
    port: int = 23
    timeout: float = 10.0


class ConnectByIdRequest(BaseModel):
    connection_id: str
    # Serial overrides
    override_port: Optional[str] = None
    override_baudrate: Optional[int] = None
    # Telnet overrides
    override_host: Optional[str] = None
    override_telnet_port: Optional[int] = None
    # Common overrides
    override_timeout: Optional[float] = None


class CommandRequest(BaseModel):
    command: str
    timeout: Optional[float] = None


@router.get("/connections")
def list_known_connections():
    """List all known device connections."""
    connections = connection_manager.get_known_connections()
    return {
        "known_connections": {
            conn_id: conn.to_dict()
            for conn_id, conn in connections.items()
        },
        "default_connection": connection_manager._default_connection,
        "count": len(connections)
    }


@router.get("/connections/{connection_id}")
def get_known_connection(connection_id: str):
    """Get details for a specific known connection."""
    connection = connection_manager.get_connection(connection_id)
    if not connection:
        raise HTTPException(
            status_code=404,
            detail=f"Connection '{connection_id}' not found"
        )
    return connection.to_dict()


@router.post("/connect/by-id")
def connect_by_id(request: ConnectByIdRequest):
    """Connect to a device using a known connection ID."""
    global current_connection

    # Get the known connection
    known_conn = connection_manager.get_connection(request.connection_id)
    if not known_conn:
        raise HTTPException(
            status_code=404,
            detail=f"Connection '{request.connection_id}' not found"
        )

    try:
        # Disconnect existing connection if any
        if current_connection:
            current_connection.disconnect()

        # Use factory to create appropriate connector
        current_connection = ConnectionFactory.create_connector(
            known_conn=known_conn,
            override_host=request.override_host,
            override_port=request.override_port,
            override_baudrate=request.override_baudrate,
            override_telnet_port=request.override_telnet_port,
            override_timeout=request.override_timeout
        )

        # Attempt to connect
        current_connection.connect()

        # Build response with connection-specific info
        if known_conn.connection_type == "telnet":
            host = request.override_host or known_conn.host
            telnet_port = (request.override_telnet_port or
                           known_conn.telnet_port)
            timeout = request.override_timeout or known_conn.timeout
            connection_info = {
                "host": host,
                "telnet_port": telnet_port,
                "timeout": timeout
            }
            logger.info(f"Successfully connected to {known_conn.name} "
                        f"at {host}:{telnet_port}")
        else:
            port = request.override_port or known_conn.port
            baudrate = request.override_baudrate or known_conn.baudrate
            timeout = request.override_timeout or known_conn.timeout
            connection_info = {
                "port": port,
                "baudrate": baudrate,
                "timeout": timeout
            }
            logger.info(f"Successfully connected to {known_conn.name} "
                        f"on {port}")

        return {
            "message": f"Successfully connected to {known_conn.name}",
            "connection_id": request.connection_id,
            "connection_name": known_conn.name,
            "description": known_conn.description,
            "connection_type": known_conn.connection_type,
            "device_type": known_conn.device_type,
            "model": known_conn.model,
            "location": known_conn.location,
            "common_commands": known_conn.common_commands,
            **connection_info
        }

    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        current_connection = None
        raise HTTPException(
            status_code=400,
            detail=f"Configuration error: {str(e)}"
        )
    except ConnectionError as e:
        logger.error(f"Connection failed: {str(e)}")
        current_connection = None
        raise HTTPException(
            status_code=400,
            detail=f"Connection failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during connection: {str(e)}")
        current_connection = None
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post("/connect/by-id/{connection_id}")
def connect_by_id_path(connection_id: str):
    """Connect to a device using a known connection ID (path parameter)."""
    # Create a request object and delegate to the main function
    request = ConnectByIdRequest(connection_id=connection_id)
    return connect_by_id(request)


@router.post("/connect/default")
def connect_to_default():
    """Connect to the default known connection."""
    default_conn = connection_manager.get_default_connection()
    if not default_conn:
        raise HTTPException(
            status_code=404,
            detail="No default connection configured"
        )

    # Use the connect_by_id function with the default connection
    request = ConnectByIdRequest(connection_id=default_conn.id)
    return connect_by_id(request)


@router.get("/connections/by-type/{device_type}")
def list_connections_by_type(device_type: str):
    """List known connections filtered by device type."""
    connections = connection_manager.list_connections_by_type(device_type)
    return {
        "device_type": device_type,
        "connections": [conn.to_dict() for conn in connections],
        "count": len(connections)
    }


@router.get("/connections/by-port/{port}")
def list_connections_by_port(port: str):
    """List known connections filtered by port."""
    connections = connection_manager.list_connections_by_port(port)
    return {
        "port": port,
        "connections": [conn.to_dict() for conn in connections],
        "count": len(connections)
    }


@router.post("/connect")
def connect_to_device(request: SerialConnectRequest = SerialConnectRequest()):
    """Connect to a device via serial port."""
    global current_connection

    try:
        # Disconnect existing connection if any
        if current_connection:
            current_connection.disconnect()

        # Use factory to create serial connector
        current_connection = ConnectionFactory.create_connector_from_params(
            connection_type="serial",
            port=request.port,
            baudrate=request.baudrate,
            timeout=request.timeout
        )

        # Attempt to connect
        current_connection.connect()

        logger.info(f"Successfully connected to {request.port}")
        return {
            "message": f"Successfully connected to {request.port}",
            "connection_type": "serial",
            "port": request.port,
            "baudrate": request.baudrate,
            "timeout": request.timeout
        }

    except ConnectionError as e:
        logger.error(f"Connection failed: {str(e)}")
        current_connection = None
        raise HTTPException(
            status_code=400,
            detail=f"Connection failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during connection: {str(e)}")
        current_connection = None
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post("/connect/telnet")
def connect_telnet(request: TelnetConnectRequest):
    """Connect to a device via telnet."""
    global current_connection

    try:
        # Disconnect existing connection if any
        if current_connection:
            current_connection.disconnect()

        # Use factory to create telnet connector
        current_connection = ConnectionFactory.create_connector_from_params(
            connection_type="telnet",
            host=request.host,
            port=request.port,
            timeout=request.timeout
        )

        # Attempt to connect
        current_connection.connect()

        logger.info(f"Successfully connected to {request.host}:{request.port}")
        return {
            "message": (f"Successfully connected to "
                        f"{request.host}:{request.port}"),
            "connection_type": "telnet",
            "host": request.host,
            "telnet_port": request.port,
            "timeout": request.timeout
        }

    except ConnectionError as e:
        logger.error(f"Telnet connection failed: {str(e)}")
        current_connection = None
        raise HTTPException(
            status_code=400,
            detail=f"Telnet connection failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during telnet connection: {str(e)}")
        current_connection = None
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@router.delete("/disconnect")
def disconnect_from_device():
    """Disconnect from the current device."""
    global current_connection

    if not current_connection:
        return {"message": "No active connection to disconnect"}

    try:
        # Get connection info before disconnecting
        if isinstance(current_connection, TelnetConnector):
            host = current_connection.host
            port = current_connection.port
            connection_info = f"{host}:{port}"
        else:
            connection_info = current_connection.port

        current_connection.disconnect()
        current_connection = None

        logger.info(f"Successfully disconnected from {connection_info}")
        return {"message": f"Successfully disconnected from {connection_info}"}

    except Exception as e:
        logger.error(f"Error during disconnection: {str(e)}")
        current_connection = None
        raise HTTPException(
            status_code=500,
            detail=f"Disconnection error: {str(e)}"
        )


@router.post("/command")
def send_command(request: CommandRequest):
    """Send a command to the connected device."""
    global current_connection

    if not current_connection:
        raise HTTPException(
            status_code=400,
            detail="No active connection. Please connect first."
        )

    try:
        response = current_connection.send_command(
            command=request.command,
            timeout=request.timeout
        )

        logger.info(f"Command '{request.command}' executed successfully")
        return {
            "command": request.command,
            "response": response,
            "status": "success"
        }

    except TimeoutError as e:
        logger.error(f"Command timeout: {str(e)}")
        raise HTTPException(
            status_code=408,
            detail=f"Command timeout: {str(e)}"
        )
    except ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        # Reset connection on connection error
        current_connection = None
        raise HTTPException(
            status_code=400,
            detail=f"Connection error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error executing command: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Command execution error: {str(e)}"
        )


@router.get("/status")
def get_connection_status():
    """Get the current connection status."""
    global current_connection

    if not current_connection:
        return {
            "connected": False,
            "connection_type": None,
            "message": "No active connection",
            "available_connections": len(
                connection_manager.get_known_connections()
            )
        }

    # Determine connection type and extract info
    if isinstance(current_connection, TelnetConnector):
        connection_type = "telnet"
        connection_info = {
            "host": current_connection.host,
            "telnet_port": current_connection.port,
            "timeout": current_connection.timeout,
            "message": f"Connected to {current_connection.host}:"
                       f"{current_connection.port}"
        }
        # Try to find matching known connection
        known_conn = None
        connections = connection_manager.get_known_connections()
        for conn_id, conn in connections.items():
            if (conn.connection_type == "telnet" and
                    conn.host == current_connection.host and
                    conn.telnet_port == current_connection.port):
                known_conn = conn
                break
    else:
        connection_type = "serial"
        connection_info = {
            "port": current_connection.port,
            "baudrate": current_connection.baudrate,
            "timeout": current_connection.timeout,
            "message": f"Connected to {current_connection.port}"
        }
        # Try to find matching known connection
        known_conn = None
        connections = connection_manager.get_known_connections()
        for conn_id, conn in connections.items():
            if (conn.connection_type == "serial" and
                    conn.port == current_connection.port and
                    conn.baudrate == current_connection.baudrate):
                known_conn = conn
                break

    status = {
        "connected": True,
        "connection_type": connection_type,
        **connection_info
    }

    if known_conn:
        status.update({
            "connection_id": known_conn.id,
            "connection_name": known_conn.name,
            "device_type": known_conn.device_type,
            "model": known_conn.model,
            "location": known_conn.location,
            "description": known_conn.description,
            "common_commands": known_conn.common_commands
        })

    return status
