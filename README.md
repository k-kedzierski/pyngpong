# Pyngpong

Simple Multiplayer Python Ping Pong game.

# Prerequisites

Install dependencies from lock file with Poetry:

```sh
poetry install
source `poetry env info --path`/bin/activate
```

# Usage

Run the game server:

*Note: if running Python 3 only, replace `python3` with `python`.*
```sh
python3 -m pingpong/server.py [--host HOST] 
                              [--port PORT]
```

Connect to server with game client:

```sh
python3 -m pingpong [--host HOST] 
                    [--port PORT]
```


For additional help, refer to `--help`

# Contributing

You don't.

# Project status

Made by Ponczek team 🍩