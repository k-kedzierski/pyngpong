from pingpong import game
import configparser


def main(config) -> None:
    game_instance = game.Game(
        width=int(config["game_size"]["width"]),
        height=int(config["game_size"]["height"])
    )

    game_instance.run()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(f"config.ini")

    main(config)
