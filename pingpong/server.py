import socket
import logging
from _thread import start_new_thread
import configparser
from typing import Tuple

logging.basicConfig(
    format=r"%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
    datefmt=r"[%Y-%m-%d %H:%M:%S %z]",
    level=logging.INFO,
)


class Server:
    def __init__(self, config_file: str) -> None:
        config = configparser.ConfigParser()
        config.read(f"{config_file}")

        self.config = config
        self.positions = [(50, 50), (200, 200)]

    def run_server(self) -> None:
        # Set up socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind socket to address and port
        server_socket.bind(
            (self.config["server"]["host"], int(self.config["server"]["port"]))
        )

        logging.info(
            "Started server on host: %s, port: %s",
            self.config["server"]["host"],
            self.config["server"]["port"],
        )

        # Listen for connections
        server_socket.listen(int(self.config["server"]["maxConnections"]))

        player_id = 0

        # Main server loop
        while True:
            # Synchronously wait for any client to connect
            connection, address = server_socket.accept()

            logging.info("Connected to: %s", address)

            start_new_thread(self.threaded_client, (connection, player_id))
            player_id += 1

    def threaded_client(self, connection, player_id) -> None:
        connection.send(str.encode(str(player_id)))

        while True:

            response = connection.recv(int(self.config["server"]["dataSize"])).decode(
                "utf-8"
            )

            if not response:
                connection.send(str.encode("Disconnected"))
                break

            player_id, pos_x, pos_y = self.parse_response(response)
            # Save the new position
            self.positions[player_id] = (pos_x, pos_y)

            # Send the position of the other player
            message = "{0}:{1}".format(
                self._next_player(player_id),
                str(self.positions[self._next_player(player_id)])[1:-1],
            )

            connection.sendall(str.encode(message))

        logging.info("Connection Closed")
        connection.close()

    def parse_response(self, response) -> Tuple[int, int, int]:
        data = response.split(":", 1)
        pos_x, pos_y = data.pop().split(",")
        return int(float(data.pop())), int(float(pos_x)), int(float(pos_y))

    def _next_player(self, player_id) -> int:
        return (player_id + 1) % len(self.positions)


if __name__ == "__main__":
    server = Server("config.ini")
    server.run_server()
