import logging
from typing import Optional

from sel.aft.streams import SerialStream

from sel.aft_shared.protocols.sel_ascii import SelAscii

from src.device.connector import (
    Connector
)


class SerialConnector(Connector):
    """Connector for serial port communication."""

    _logger = logging.getLogger(__name__)

    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 10):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None

    def connect(self) -> bool:
        self.serial = SerialStream(
            port=self.port,
            baud=self.baudrate,
            readtimeout=int(self.timeout * 1000)  # Convert to milliseconds
        )
        self.serial.open()
        SerialConnector._logger.info(f"Successfully connected to serial port {self.port}")
        return True

    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
            SerialConnector._logger.info(f"Disconnected from serial port {self.port}")

    def send_command(
        self, command: str, timeout: Optional[float] = None
    ) -> str:
        if not self.serial or not self.serial.is_open:
            error_msg = "Cannot send command - serial port is not connected"
            SerialConnector._logger.error(error_msg)
            raise ConnectionError(error_msg)

        # Use default timeout if none provided, convert to milliseconds
        if timeout is None:
            timeout_ms = None  # Let protocol use its default
        else:
            timeout_ms = int(timeout * 1000)

        # Clear any pending input.
        self.serial.listen(wait_time=50)

        # Send the command
        protocol = SelAscii(self.serial)
        SerialConnector._logger.debug(f"Sending command: {command.strip()}")
        resp = protocol.send(command, read_timeout=timeout_ms)
        SerialConnector._logger.debug(f"Received response: {resp.strip()}")

        return resp
