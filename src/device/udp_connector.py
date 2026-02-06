import logging
from typing import Optional

from sel.aft.streams import UdpStream

from src.device.connector import Connector, ConnectionError


class UdpConnector(Connector):
    """Connector for UDP communication (e.g., HiPTAP)."""

    _logger = logging.getLogger(__name__)

    def __init__(
        self,
        host: str,
        port: int = 34566,
        timeout: float = 10,
        stream_type: Optional[str] = None,
        protocol: Optional[str] = None
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.stream_type = stream_type
        self.protocol = protocol
        self.udp = None

    def connect(self) -> bool:
        self.udp = UdpStream(
            host=self.host,
            port=int(self.port),
            readtimeout=int(self.timeout * 1000)
        )
        self.udp.open()
        UdpConnector._logger.info(
            f"Successfully connected to UDP {self.host}:{self.port}"
        )
        return True

    def disconnect(self) -> None:
        if self.udp and self.udp.is_open:
            self.udp.close()
            UdpConnector._logger.info(
                f"Disconnected from UDP {self.host}:{self.port}"
            )
            self.udp = None

    def send_command(self, command: str, timeout: Optional[float] = None) -> str:
        if not self.udp or not self.udp.is_open:
            error_msg = "Cannot send command - UDP connection is not established"
            UdpConnector._logger.error(error_msg)
            raise ConnectionError(error_msg)

        # Use default timeout if none provided, convert to milliseconds
        if timeout is None:
            timeout_ms = None
        else:
            timeout_ms = int(timeout * 1000)

        payload = command.encode("utf-8")
        UdpConnector._logger.debug(
            f"Sending UDP command to {self.host}:{self.port}: {command.strip()}"
        )
        reply = self.udp.send(payload, read_timeout=timeout_ms)
        if not reply:
            return ""
        try:
            return reply.decode("utf-8", errors="replace")
        except Exception:
            return str(reply)
