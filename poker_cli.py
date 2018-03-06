import logging

from human_player import HumanPlayer
from poker import Table


_red = "\x1b[31m["
_normal = "\x1b[0m"


def main():
    logging.basicConfig(
        format=_red + "%(levelname)s][%(asctime)s] %(message)s" + _normal,
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO
    )

    players = [HumanPlayer(i) for i in range(3)]
    table = Table(players, 8000, 25)
    table.play()


if __name__ == "__main__":
    main()
