
import logging
from sel.aft.streams import TelnetStream
from sel.aft_shared.protocols import SelAscii

from src.device.connector import Connector


class TelnetConnector(Connector):
    """Connector for Telnet communication."""

    _logger = logging.getLogger(__name__)

    def __init__(self, host: str, port: int = 23, timeout: float = 10):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.telnet = None

    def connect(self) -> bool:
        self.telnet = TelnetStream(
            host=self.host,
            port=self.port,
            timeout=int(self.timeout * 1000)
        )
        self.telnet.open()
        return True

    def disconnect(self) -> None:
        if self.telnet:
            self.telnet.close()
            self.telnet = None

    def send_command(self, command: str, timeout: float | None = None) -> str:
        if not self.telnet or not self.telnet.is_open:
            error_msg = "Cannot send command - telnet connection is not established"
            TelnetConnector._logger.error(error_msg)
            raise ConnectionError(error_msg)

        # Use default timeout if none provided, convert to milliseconds
        if timeout is None:
            timeout_ms = None  # Let protocol use its default
        else:
            timeout_ms = int(timeout * 1000)

        # Clear any pending input.
        self.telnet.listen(wait_time=50)

        # Send the command
        protocol = SelAscii(self.telnet)
        TelnetConnector._logger.debug(f"Sending command: {command.strip()}")
        resp = protocol.send(command, read_timeout=timeout_ms)
        TelnetConnector._logger.debug(f"Received response: {resp.strip()}")

        return resp
