from abc import ABC, abstractmethod

class Connector(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def send_command(self, command):
        pass
