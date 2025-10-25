from src.device.connector import Connector

class MCP:
    def __init__(self, connector: Connector):
        self.connector = connector

    def connect(self):
        self.connector.connect()

    def disconnect(self):
        self.connector.disconnect()

    def send_command(self, command):
        return self.connector.send_command(command)
