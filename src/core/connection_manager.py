"""
Configuration manager for known device connections.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class KnownConnection:
    """Represents a known device connection configuration."""
    id: str
    name: str
    description: str
    device_type: str
    model: str
    location: str
    common_commands: List[str]
    timeout: float = 10.0
    
    # Serial connection fields
    port: Optional[str] = None
    baudrate: Optional[int] = None
    
    # Telnet connection fields
    host: Optional[str] = None
    telnet_port: Optional[int] = None
    
    # Optional prompts (can be empty)
    prompts: Optional[List[str]] = None
    
    @property
    def connection_type(self) -> str:
        """Determine connection type based on available fields."""
        if self.host is not None:
            return "telnet"
        elif self.port is not None:
            return "serial"
        else:
            return "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "device_type": self.device_type,
            "model": self.model,
            "location": self.location,
            "common_commands": self.common_commands,
            "timeout": self.timeout,
            "connection_type": self.connection_type
        }
        
        # Add connection-specific fields
        if self.connection_type == "serial":
            result.update({
                "port": self.port,
                "baudrate": self.baudrate
            })
        elif self.connection_type == "telnet":
            result.update({
                "host": self.host,
                "telnet_port": self.telnet_port
            })
        
        # Add prompts if they exist
        if self.prompts:
            result["prompts"] = self.prompts
            
        return result


class ConnectionManager:
    """Manages known device connections and profiles."""

    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)

        if config_path is None:
            # Default to config file in project root
            project_root = Path(__file__).parent.parent.parent
            config_file = project_root / "config" / "known_connections.json"
            config_path = str(config_file)

        self.config_path = Path(config_path)
        self._known_connections: Dict[str, KnownConnection] = {}
        self._connection_profiles: Dict[str, Dict[str, Any]] = {}
        self._default_connection: Optional[str] = None

        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from JSON file."""
        try:
            if not self.config_path.exists():
                self.logger.warning(
                    f"Config file not found: {self.config_path}"
                )
                return

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Load known connections
            known_connections = config.get("known_connections", {})
            for conn_id, conn_data in known_connections.items():
                # Determine connection type and extract appropriate fields
                if "host" in conn_data:
                    # Telnet connection
                    port_value = conn_data.get("port")
                    telnet_port = int(port_value) if port_value else 23
                    connection = KnownConnection(
                        id=conn_id,
                        name=conn_data.get("name", ""),
                        description=conn_data.get("description", ""),
                        device_type=conn_data.get("device_type", "GENERIC"),
                        model=conn_data.get("model", "Unknown"),
                        location=conn_data.get("location", "Unknown"),
                        common_commands=conn_data.get("common_commands", []),
                        timeout=conn_data.get("timeout", 10.0),
                        host=conn_data.get("host"),
                        telnet_port=telnet_port,
                        prompts=conn_data.get("prompts")
                    )
                else:
                    # Serial connection
                    connection = KnownConnection(
                        id=conn_id,
                        name=conn_data.get("name", ""),
                        description=conn_data.get("description", ""),
                        device_type=conn_data.get("device_type", "GENERIC"),
                        model=conn_data.get("model", "Unknown"),
                        location=conn_data.get("location", "Unknown"),
                        common_commands=conn_data.get("common_commands", []),
                        timeout=conn_data.get("timeout", 10.0),
                        port=conn_data.get("port", "COM1"),
                        baudrate=conn_data.get("baudrate", 9600),
                        prompts=conn_data.get("prompts", [">"])
                    )
                
                self._known_connections[conn_id] = connection

            # Load connection profiles
            self._connection_profiles = config.get("connection_profiles", {})

            # Load default connection
            self._default_connection = config.get("default_connection")

            self.logger.info(
                f"Loaded {len(self._known_connections)} known connections"
            )

        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")

    def get_known_connections(self) -> Dict[str, KnownConnection]:
        """Get all known connections."""
        return self._known_connections.copy()

    def get_connection(self, connection_id: str) -> Optional[KnownConnection]:
        """Get a specific known connection by ID."""
        return self._known_connections.get(connection_id)

    def get_default_connection(self) -> Optional[KnownConnection]:
        """Get the default connection."""
        if self._default_connection:
            return self.get_connection(self._default_connection)
        return None

    def get_connection_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get all connection profiles."""
        return self._connection_profiles.copy()

    def list_connections_by_type(
        self, device_type: str
    ) -> List[KnownConnection]:
        """Get all connections of a specific device type."""
        return [
            conn for conn in self._known_connections.values()
            if conn.device_type == device_type
        ]

    def list_connections_by_port(self, port: str) -> List[KnownConnection]:
        """Get all connections using a specific port."""
        return [
            conn for conn in self._known_connections.values()
            if conn.port == port
        ]

    def add_connection(self, connection: KnownConnection) -> None:
        """Add a new known connection (runtime only, not persisted)."""
        self._known_connections[connection.id] = connection
        self.logger.info(f"Added connection: {connection.id}")

    def remove_connection(self, connection_id: str) -> bool:
        """Remove a known connection (runtime only, not persisted)."""
        if connection_id in self._known_connections:
            del self._known_connections[connection_id]
            self.logger.info(f"Removed connection: {connection_id}")
            return True
        return False


# Global connection manager instance
connection_manager = ConnectionManager()
