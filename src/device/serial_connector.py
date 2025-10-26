import logging
import re
import serial
import time
from typing import Optional

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

    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1,
                 prompts: Optional[list[str]] = None):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.prompts = prompts if prompts is not None else self.DEFAULT_PROMPTS
        self._prompt_pattern = re.compile('|'.join(self.prompts))

    def connect(self):
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            SerialConnector._logger.info(f"Successfully connected to serial port {self.port}")
            return True
        except serial.SerialException as e:
            error_msg = (
                f"Failed to connect to serial port {self.port}: {str(e)}"
            )
            SerialConnector._logger.error(error_msg)
            raise SerialConnectionError(error_msg) from e

    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
            SerialConnector._logger.info(f"Disconnected from serial port {self.port}")

    def _read_until_prompt(self, timeout: Optional[float] = None) -> str:
        """Read from serial port until a prompt is found or timeout occurs."""
        timeout = timeout if timeout is not None else self.timeout
        response: list[str] = []
        start_time = time.time()
        assert self.serial is not None, "Serial port is not connected"

        while True:
            if time.time() - start_time > timeout:
                error_msg = (
                    f"Timeout waiting for prompt after {timeout} seconds"
                )
                SerialConnector._logger.error(error_msg)
                raise SerialTimeoutError(error_msg)

            if self.serial.in_waiting:
                char = self.serial.read().decode('utf-8', errors='replace')
                response.append(char)

                # Check for prompt in the accumulated response
                full_response = ''.join(response)
                if self._prompt_pattern.search(full_response):
                    return full_response

            time.sleep(0.01)  # Short sleep to prevent CPU spinning

    def send_command(
        self, command: str, timeout: Optional[float] = None
    ) -> str:
        if not self.serial or not self.serial.is_open:
            error_msg = "Cannot send command - serial port is not connected"
            SerialConnector._logger.error(error_msg)
            raise SerialConnectionError(error_msg)

        try:
            # Convert string to bytes and append newline if needed
            if not command.endswith('\n'):
                command += '\n'
            encoded_command = command.encode('utf-8')

            # Clear any pending input
            self.serial.reset_input_buffer()

            # Send the command
            self.serial.write(encoded_command)
            self.serial.flush()
            SerialConnector._logger.debug(f"Sent command: {command.strip()}")

            # Read until prompt
            response = self._read_until_prompt(timeout)
            SerialConnector._logger.debug(f"Received response: {response.strip()}")
            return response

        except serial.SerialException as e:
            error_msg = f"Failed to send command: {str(e)}"
            SerialConnector._logger.error(error_msg)
            raise SerialConnectionError(error_msg) from e
