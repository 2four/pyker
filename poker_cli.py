import logging

from human_player import HumanPlayer
from network_player import NetworkPlayer
from poker import Table


_red = "\x1b[31m["
_normal = "\x1b[0m"


def main():
    logging.basicConfig(
        format=_red + "%(levelname)s][%(asctime)s] %(message)s" + _normal,
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.DEBUG
    )

    players = [HumanPlayer() for i in range(3)]
    # players.append(NetworkPlayer(None, 15, 4, 25))
    table = Table(players, 8000, 25)
    table.play()


if __name__ == "__main__":
    main()
