"""
Connection factory for creating appropriate connector instances.
"""

import logging
from typing import Optional, Union

from ..device.serial_connector import SerialConnector
from ..device.telnet_connector import TelnetConnector
from ..device.udp_connector import UdpConnector
from ..device.tcp_connector import TcpConnector
from ..device.connector import Connector
from .connection_manager import KnownConnection


class ConnectionFactory:
    """Factory for creating connector instances from known connections."""

    _logger = logging.getLogger(__name__)

    @classmethod
    def create_connector(
        cls,
        known_conn: KnownConnection,
        override_host: Optional[str] = None,
        override_port: Optional[str] = None,
        override_baudrate: Optional[int] = None,
        override_telnet_port: Optional[int] = None,
        override_udp_port: Optional[int] = None,
        override_timeout: Optional[float] = None
    ) -> Union[SerialConnector, TelnetConnector, UdpConnector, TcpConnector]:
        """
        Create appropriate connector based on known connection type.

        Args:
            known_conn: The known connection configuration
            override_host: Override host for telnet connections
            override_port: Override COM port for serial connections
            override_baudrate: Override baudrate for serial connections
            override_telnet_port: Override port for telnet connections
            override_timeout: Override timeout for any connection

        Returns:
            Appropriate connector instance

        Raises:
            ValueError: If connection type is unknown or missing required
                       fields
        """

        if known_conn.connection_type == "telnet":
            return cls._create_telnet_connector(
                known_conn, override_host, override_telnet_port,
                override_timeout
            )
        elif known_conn.connection_type == "serial":
            return cls._create_serial_connector(
                known_conn, override_port, override_baudrate, override_timeout
            )
        elif known_conn.connection_type == "tcp":
            return cls._create_tcp_connector(
                known_conn,
                override_host,
                override_port,
                override_timeout
            )
        elif known_conn.connection_type == "udp":
            return cls._create_udp_connector(
                known_conn,
                override_host,
                override_udp_port or override_port,
                override_timeout
            )
        else:
            raise ValueError(
                f"Unknown connection type: {known_conn.connection_type}"
            )

    @classmethod
    def _create_telnet_connector(
        cls,
        known_conn: KnownConnection,
        override_host: Optional[str] = None,
        override_telnet_port: Optional[int] = None,
        override_timeout: Optional[float] = None
    ) -> TelnetConnector:
        """Create a telnet connector."""

        # Use override values or fall back to known connection values
        host = override_host or known_conn.host
        telnet_port = override_telnet_port or known_conn.telnet_port
        timeout = override_timeout or known_conn.timeout

        # Validate required fields
        if not host:
            raise ValueError(
                f"Host is required for telnet connection '{known_conn.id}'"
            )
        if not telnet_port:
            raise ValueError(
                f"Port is required for telnet connection '{known_conn.id}'"
            )

        cls._logger.info(
            f"Creating telnet connector for {known_conn.name} "
            f"({host}:{telnet_port})"
        )

        return TelnetConnector(
            host=host,
            port=telnet_port,
            timeout=timeout
        )

    @classmethod
    def _create_serial_connector(
        cls,
        known_conn: KnownConnection,
        override_port: Optional[str] = None,
        override_baudrate: Optional[int] = None,
        override_timeout: Optional[float] = None
    ) -> SerialConnector:
        """Create a serial connector."""

        # Use override values or fall back to known connection values
        port = override_port or known_conn.port
        baudrate = override_baudrate or known_conn.baudrate
        timeout = override_timeout or known_conn.timeout

        # Validate required fields
        if not port:
            raise ValueError(
                f"Port is required for serial connection '{known_conn.id}'"
            )
        if not baudrate:
            raise ValueError(
                f"Baudrate is required for serial connection '{known_conn.id}'"
            )

        # Handle prompts - use provided prompts or default
        prompts = known_conn.prompts if known_conn.prompts else [">"]

        cls._logger.info(
            f"Creating serial connector for {known_conn.name} "
            f"({port} @ {baudrate} baud)"
        )

        return SerialConnector(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            prompts=prompts
        )

    @classmethod
    def _create_udp_connector(
        cls,
        known_conn: KnownConnection,
        override_host: Optional[str] = None,
        override_udp_port: Optional[int] = None,
        override_timeout: Optional[float] = None
    ) -> UdpConnector:
        """Create a UDP connector."""

        host = override_host or known_conn.host
        udp_port = override_udp_port or known_conn.udp_port
        timeout = override_timeout or known_conn.timeout

        if not host:
            raise ValueError(
                f"Host is required for UDP connection '{known_conn.id}'"
            )
        if not udp_port:
            raise ValueError(
                f"Port is required for UDP connection '{known_conn.id}'"
            )

        cls._logger.info(
            f"Creating UDP connector for {known_conn.name} "
            f"({host}:{udp_port})"
        )

        return UdpConnector(
            host=host,
            port=int(udp_port),
            timeout=timeout,
            stream_type=known_conn.stream_type,
            protocol=known_conn.protocol
        )

    @classmethod
    def _create_tcp_connector(
        cls,
        known_conn: KnownConnection,
        override_host: Optional[str] = None,
        override_tcp_port: Optional[int] = None,
        override_timeout: Optional[float] = None
    ) -> TcpConnector:
        """Create a TCP connector."""

        host = override_host or known_conn.host
        tcp_port = override_tcp_port or known_conn.tcp_port
        timeout = override_timeout or known_conn.timeout

        if not host:
            raise ValueError(
                f"Host is required for TCP connection '{known_conn.id}'"
            )
        if not tcp_port:
            raise ValueError(
                f"Port is required for TCP connection '{known_conn.id}'"
            )

        cls._logger.info(
            f"Creating TCP connector for {known_conn.name} "
            f"({host}:{tcp_port})"
        )

        return TcpConnector(
            host=host,
            port=int(tcp_port),
            timeout=timeout,
            stream_type=known_conn.stream_type,
            protocol=known_conn.protocol
        )

    @classmethod
    def create_connector_from_params(
        cls,
        connection_type: str,
        **kwargs
    ) -> Union[SerialConnector, TelnetConnector, UdpConnector, TcpConnector]:
        """
        Create connector directly from parameters.

        Args:
            connection_type: 'serial' or 'telnet'
            **kwargs: Connection parameters

        Returns:
            Appropriate connector instance
        """

        if connection_type == "telnet":
            host = kwargs.get("host")
            port = kwargs.get("port", 23)
            timeout = kwargs.get("timeout", 10.0)

            if not host:
                raise ValueError("Host is required for telnet connection")

            cls._logger.info(f"Creating telnet connector ({host}:{port})")
            return TelnetConnector(host=host, port=port, timeout=timeout)

        elif connection_type == "serial":
            port = kwargs.get("port")
            baudrate = kwargs.get("baudrate", 9600)
            timeout = kwargs.get("timeout", 10.0)
            prompts = kwargs.get("prompts", [">"])

            if not port:
                raise ValueError("Port is required for serial connection")

            cls._logger.info(f"Creating serial connector ({port} @ {baudrate})")
            return SerialConnector(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                prompts=prompts
            )

        elif connection_type == "udp":
            host = kwargs.get("host")
            port = kwargs.get("port", 34566)
            timeout = kwargs.get("timeout", 10.0)
            stream_type = kwargs.get("stream_type")
            protocol = kwargs.get("protocol")

            if not host:
                raise ValueError("Host is required for UDP connection")

            cls._logger.info(f"Creating UDP connector ({host}:{port})")
            return UdpConnector(
                host=host,
                port=int(port),
                timeout=timeout,
                stream_type=stream_type,
                protocol=protocol
            )

        elif connection_type == "tcp":
            host = kwargs.get("host")
            port = kwargs.get("port", 9005)
            timeout = kwargs.get("timeout", 10.0)
            stream_type = kwargs.get("stream_type")
            protocol = kwargs.get("protocol")

            if not host:
                raise ValueError("Host is required for TCP connection")

            cls._logger.info(f"Creating TCP connector ({host}:{port})")
            return TcpConnector(
                host=host,
                port=int(port),
                timeout=timeout,
                stream_type=stream_type,
                protocol=protocol
            )

        else:
            raise ValueError(f"Unknown connection type: {connection_type}")


# Convenience function for creating connectors
def create_connector(known_conn: KnownConnection, **overrides) -> Connector:
    """Convenience function to create connector from known connection."""
    return ConnectionFactory.create_connector(known_conn, **overrides)
