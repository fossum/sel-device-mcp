import logging
from typing import Optional

from sel.aft.streams import TcpStream

from src.device.connector import Connector, ConnectionError


class TcpConnector(Connector):
    """Connector for TCP communication (e.g., HiPTAP)."""

    _logger = logging.getLogger(__name__)

    def __init__(
        self,
        host: str,
        port: int = 9005,
        timeout: float = 10,
        stream_type: Optional[str] = None,
        protocol: Optional[str] = None
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.stream_type = stream_type
        self.protocol = protocol
        self.tcp = None

    def connect(self) -> bool:
        self.tcp = TcpStream(
            host=self.host,
            port=int(self.port),
            readtimeout=int(self.timeout * 1000)
        )
        self.tcp.open()
        TcpConnector._logger.info(
            f"Successfully connected to TCP {self.host}:{self.port}"
        )
        return True

    def disconnect(self) -> None:
        if self.tcp and self.tcp.is_open:
            self.tcp.close()
            TcpConnector._logger.info(
                f"Disconnected from TCP {self.host}:{self.port}"
            )
            self.tcp = None

    def send_command(self, command: str, timeout: Optional[float] = None) -> str:
        if not self.tcp or not self.tcp.is_open:
            error_msg = "Cannot send command - TCP connection is not established"
            TcpConnector._logger.error(error_msg)
            raise ConnectionError(error_msg)

        # Use default timeout if none provided, convert to milliseconds
        if timeout is None:
            timeout_ms = None
        else:
            timeout_ms = int(timeout * 1000)

        payload = command.encode("utf-8")
        TcpConnector._logger.debug(
            f"Sending TCP command to {self.host}:{self.port}: {command.strip()}"
        )
        reply = self.tcp.send(payload, read_timeout=timeout_ms)
        if not reply:
            return ""
        try:
            return reply.decode("utf-8", errors="replace")
        except Exception:
            return str(reply)
