from human_player import HumanPlayer
from poker import Table


def main():
    players = [HumanPlayer(i) for i in range(3)]
    table = Table(players, 8000, 25)
    table.play()


if __name__ == "__main__":
    main()
