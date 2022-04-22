import socket
import logging
from _thread import start_new_thread
import configparser
import argparse
from typing import Tuple

logging.basicConfig(
    format=r"%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
    datefmt=r"[%Y-%m-%d %H:%M:%S %z]",
    level=logging.INFO,
)


class Server:
    def __init__(self, config, args) -> None:
        self.config = config
        self.args = args
        self.positions = [(50, 50), (200, 200)]

    def run_server(self) -> None:
        # Set up socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind socket to address and port
        server_socket.bind((self.args.host, self.args.port))

        logging.info(
            "Started server on host: %s, port: %s",
            self.args.host,
            self.args.port,
        )

        # Listen for connections
        server_socket.listen(int(self.config["server"]["maxConnections"]))

        # Player ID counter allows us to keep track of the players and reconnect
        # if the client closes the connection
        self._player_id = 0

        # Main server loop
        while True:
            # Synchronously wait for any client to connect
            connection, address = server_socket.accept()

            logging.info("Connected to: %s", address)

            start_new_thread(self.threaded_client, (connection, self._player_id))
            self._player_id += 1

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

        self._player_id -= 1
        connection.close()

    def parse_response(self, response) -> Tuple[int, int, int]:
        data = response.split(":", 1)
        pos_x, pos_y = data.pop().split(",")
        return int(float(data.pop())), int(float(pos_x)), int(float(pos_y))

    def _next_player(self, player_id) -> int:
        return (player_id + 1) % len(self.positions)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(f"config.ini")

    argparser = argparse.ArgumentParser("Pyng Pong Server")
    argparser.add_argument(
        "--host", type=str, default="localhost", help="Host to run the server on"
    )
    argparser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Port to which the server will listen",
    )

    args = argparser.parse_args()

    server = Server(config, args)
    try:
        server.run_server()
    except KeyboardInterrupt:
        logging.info("Shutting down server...")
