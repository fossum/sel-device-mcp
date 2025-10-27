import logging
import re
from typing import Optional

from sel.aft.streams import SerialStream

from sel.aft_shared.protocols.sel_ascii import SelAscii

from src.device.connector import (
    Connector, SerialConnectionError, SerialTimeoutError
)


class SerialConnector(Connector):
    # Common SEL device prompts
    DEFAULT_PROMPTS = [
        r'=>\s*$',  # SEL-protocol prompt
        r'>\s*$',   # Basic prompt
    ]
    _logger = logging.getLogger(__name__)

    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 10,
                 prompts: Optional[list[str]] = None):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.prompts = prompts if prompts is not None else self.DEFAULT_PROMPTS
        self._prompt_pattern = re.compile('|'.join(self.prompts))

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
            raise SerialConnectionError(error_msg)

        # Clear any pending input.
        self.serial.listen(wait_time=50)

        # Send the command
        protocol = SelAscii(self.serial)
        SerialConnector._logger.debug(f"Sending command: {command.strip()}")
        resp = protocol.send(command)
        SerialConnector._logger.debug(f"Received response: {resp.strip()}")

        return resp
