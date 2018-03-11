import _MultiNEAT as NEAT
from math import ceil, log2
import random
import logging

from copy import deepcopy
from poker import Table
from network_player import NetworkPlayer

_action_vector_size = 3
_card_vector_size = 13 + 4
_red = "\x1b[31m"
_normal = "\x1b[0m"


class Game:

    LOGGER = logging.getLogger(name="Game")

    def __init__(self, players, table_size, buy_in, min_denomination):
        self.players = players
        self.table_size = table_size
        self.buy_in = buy_in
        self.min_denomination = min_denomination

    def play(self):
        self.LOGGER.info("NEW GAME")
        tables = self.get_tables()

        for table in tables:
            table.start()

        for table in tables:
            table.join()

    def get_tables(self):
        shuffled_players = list(self.players)
        random.shuffle(shuffled_players)
        tables = []

        # split into groups of {self.table_size}
        while len(shuffled_players) > self.table_size * 2:
            player_group = [shuffled_players.pop() for _ in range(self.table_size)]
            table = Table(player_group, self.buy_in, self.min_denomination)
            tables.append(table)

        # split the last few into two roughly even groups
        penultimate_group_size = len(shuffled_players) // 2
        penultimate_group = [shuffled_players.pop() for _ in range(penultimate_group_size)]
        table = Table(penultimate_group, self.buy_in, self.min_denomination)
        tables.append(table)

        table = Table(shuffled_players, self.buy_in, self.min_denomination)
        tables.append(table)

        return tables


class VectorParameters:

    def __init__(self, table_size, buy_in, min_denomination):
        self.table_size = table_size
        self.buy_in = buy_in
        self.min_denomination = min_denomination

        self.set_card_vector_size()
        self.set_money_vector_size()
        self.set_action_vector_size()
        self.set_in_vector_size()

    def set_card_vector_size(self):
        self.card_vector_size = _card_vector_size

    def set_money_vector_size(self):
        normalized_max_chips = self.buy_in * self.table_size // self.min_denomination
        self.money_vector_size = ceil(log2(normalized_max_chips))

    def set_action_vector_size(self):
        self.action_vector_size = _action_vector_size + self.money_vector_size

    def set_in_vector_size(self):
        size = 0

        # hold cards
        size += 2 * self.card_vector_size

        # player bet
        size += self.money_vector_size

        # table cards
        size += 5 * self.card_vector_size

        # pot
        size += self.money_vector_size

        # current bet
        size += self.money_vector_size

        # player chips
        size += self.table_size * self.card_vector_size

        # turn indicator
        size += self.table_size

        # folded indicator
        size += self.table_size

        # last action
        size += self.action_vector_size

        self.in_vector_size = size


class Tournament:

    LOGGER = logging.getLogger(name="Tournament")

    def __init__(self, population, table_size, money_vector_size, buy_in, min_denomination, num_rounds):
        self.population = population
        self.table_size = table_size
        self.money_vector_size = money_vector_size
        self.buy_in = buy_in
        self.min_denomination = min_denomination
        self.num_rounds = num_rounds
        self.create_players()

    def create_players(self):
        self.players = []
        num_genomes = self.population.NumGenomes()
        for genome_index in range(num_genomes):
            genome = self.population.AccessGenomeByIndex(genome_index)
            player = NetworkPlayer(genome, self.table_size, self.money_vector_size, self.min_denomination)
            self.players.append(player)

    def play(self):
        self.LOGGER.info("NEW TOURNAMENT")
        for round in range(self.num_rounds):
            game = Game(self.players, self.table_size, self.buy_in, self.min_denomination)
            game.play()

        for player in self.players:
            player.genome.SetEvaluated()


class PlayOff:

    LOGGER = logging.getLogger(name="PlayOff")

    def __init__(self, previous_best_genomes, current_best_genomes, table_size, money_vector_size, buy_in, min_denomination, num_rounds):
        self.previous_best_genomes = previous_best_genomes
        self.current_best_genomes = current_best_genomes
        self.table_size = table_size
        self.money_vector_size = money_vector_size
        self.buy_in = buy_in
        self.min_denomination = min_denomination
        self.num_rounds = num_rounds
        self.create_players()

    def create_players(self):
        self.players = []
        self.previous_players = []
        self.current_players = []

        for genome in self.previous_best_genomes:
            player = NetworkPlayer(genome, self.table_size, self.money_vector_size, self.min_denomination)
            self.players.append(player)
            self.previous_players.append(player)

        for genome in self.current_best_genomes:
            player = NetworkPlayer(genome, self.table_size, self.money_vector_size, self.min_denomination)
            self.players.append(player)
            self.current_players.append(player)

    def play(self):
        for player in self.players:
            player.genome.SetFitness(0)

        self.LOGGER.info("NEW PLAYOFF")
        for round in range(self.num_rounds):
            table = Table(self.players, self.buy_in, self.min_denomination)
            table.play()

        previous_genome_score = sum(player.genome.GetFitness() for player in self.previous_players)
        current_genome_score = sum(player.genome.GetFitness() for player in self.current_players)
        difference = current_genome_score - previous_genome_score
        self.LOGGER.warn("Score difference between best players: {}".format(difference))


def _get_best_n_genomes(population, n):
    num_genomes = population.NumGenomes()
    genomes = [population.AccessGenomeByIndex(genome_index) for genome_index in range(num_genomes)]
    genomes.sort(key=lambda genome: genome.GetFitness(), reverse=True)
    return [deepcopy(genome) for genome in genomes[:n]]


def main():
    logging.basicConfig(
        format=_red + "[%(levelname)s][%(asctime)s][%(name)s] %(message)s" + _normal,
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.WARN
    )

    table_size = 8
    buy_in = 8000
    min_denomination = 25
    tournament_rounds = 10

    vector_parameters = VectorParameters(table_size, buy_in, min_denomination)
    neat_parameters = NEAT.Parameters()
    genome = NEAT.Genome(
        0,
        vector_parameters.in_vector_size,
        0,
        vector_parameters.action_vector_size,
        False,
        NEAT.ActivationFunction.UNSIGNED_SIGMOID,
        NEAT.ActivationFunction.UNSIGNED_SIGMOID,
        0,
        neat_parameters,
        0
    )

    # the 0 is the RNG seed
    population = NEAT.Population(genome, neat_parameters, True, 1.0, 0)
    previous_best_genomes = None
    current_best_genomes = None

    # run for 100 generations
    for generation in range(100):
        tournament = Tournament(
            population,
            table_size,
            vector_parameters.money_vector_size,
            buy_in,
            min_denomination,
            tournament_rounds
        )

        tournament.play()

        if not current_best_genomes:
            current_best_genomes = _get_best_n_genomes(population, table_size // 2)
        else:
            previous_best_genomes = current_best_genomes
            current_best_genomes = _get_best_n_genomes(population, table_size // 2)

        if previous_best_genomes:
            playoff = PlayOff(
                current_best_genomes,
                previous_best_genomes,
                table_size,
                vector_parameters.money_vector_size,
                buy_in,
                min_denomination,
                tournament_rounds
            )
            playoff.play()

        population.Epoch()


if __name__  == "__main__":
    main()
