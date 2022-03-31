import socket
import configparser

class Network:

    def __init__(self, host: str, port: int):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

        config = configparser.ConfigParser()
        config.read(f"config.ini")
        self.config = config

        self.id = self.connect()

    def connect(self):
        self.client.connect((self.host, self.port))
        return self.client.recv(int(self.config['server']['dataSize'])).decode()

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return self.client.recv(int(self.config['server']['dataSize'])).decode()
        except socket.error as e:
            return str(e)