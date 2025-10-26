from abc import ABC, abstractmethod
from typing import Optional


class SerialConnectionError(Exception):
    """Raised when serial port connection fails"""
    pass


class SerialTimeoutError(Exception):
    """Raised when a serial operation times out"""
    pass


class Connector(ABC):
    """Abstract base class for device communication connectors.

    This class defines the interface for connecting to and communicating with
    devices through various protocols (e.g., serial, telnet). Implementers must
    provide concrete implementations of all abstract methods.
    """

    @abstractmethod
    def connect(self) -> bool:
        """Establish a connection to the device.

        Returns:
            bool: True if connection was successful, False otherwise.

        Raises:
            ConnectionError: If connection attempt fails.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close the connection to the device.

        This method should safely clean up any resources used by the
        connection. It should not raise exceptions even if the connection is
        already closed.
        """
        pass

    @abstractmethod
    def send_command(
        self, command: str, timeout: Optional[float] = None
    ) -> str:
        """Send a command to the device and wait for a response.

        Args:
            command: The command string to send to the device.
            timeout: Optional timeout in seconds. If None, use connector
                default.

        Returns:
            str: The response received from the device, including any prompt.

        Raises:
            ConnectionError: If the connection is not established or fails.
            TimeoutError: If the device does not respond within the timeout
                period.
        """
        pass
