
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

from pydantic import BaseModel

from ..device.serial_connector import SerialConnector
from ..device.connector import SerialConnectionError, SerialTimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Global connection manager
current_connection: Optional[SerialConnector] = None


class ConnectRequest(BaseModel):
    port: str = "COM5"
    baudrate: int = 9600
    timeout: float = 10


class CommandRequest(BaseModel):
    command: str
    timeout: Optional[float] = None


@router.post("/connect")
def connect_to_device(request: ConnectRequest = ConnectRequest()):
    """Connect to a device via serial port."""
    global current_connection

    try:
        # Disconnect existing connection if any
        if current_connection:
            current_connection.disconnect()

        # Create new connection
        current_connection = SerialConnector(
            port=request.port,
            baudrate=request.baudrate,
            timeout=request.timeout
        )

        # Attempt to connect
        current_connection.connect()

        logger.info(f"Successfully connected to {request.port}")
        return {
            "message": f"Successfully connected to {request.port}",
            "port": request.port,
            "baudrate": request.baudrate,
            "timeout": request.timeout
        }

    except SerialConnectionError as e:
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


@router.post("/disconnect")
def disconnect_from_device():
    """Disconnect from the current device."""
    global current_connection

    if not current_connection:
        return {"message": "No active connection to disconnect"}

    try:
        current_connection.disconnect()
        port = current_connection.port
        current_connection = None

        logger.info(f"Successfully disconnected from {port}")
        return {"message": f"Successfully disconnected from {port}"}

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

    except SerialTimeoutError as e:
        logger.error(f"Command timeout: {str(e)}")
        raise HTTPException(
            status_code=408,
            detail=f"Command timeout: {str(e)}"
        )
    except SerialConnectionError as e:
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
            "port": None,
            "message": "No active connection"
        }

    return {
        "connected": True,
        "port": current_connection.port,
        "baudrate": current_connection.baudrate,
        "timeout": current_connection.timeout,
        "message": f"Connected to {current_connection.port}"
    }
