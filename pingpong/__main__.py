from pingpong import game
import configparser
import argparse


def main(config, args) -> None:
    game_instance = game.Game(
        width=int(config["game_size"]["width"]),
        height=int(config["game_size"]["height"]),
        host=args.host,
        port=args.port,
    )

    game_instance.run()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(f"config.ini")

    argparser = argparse.ArgumentParser("Ping Pong Client")
    argparser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Server host to connect to"
    )
    argparser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Port of the server to connect to"
    )

    args = argparser.parse_args()

    main(config, args)
