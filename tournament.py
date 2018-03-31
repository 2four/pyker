from network_player import NetworkPlayer
import logging
import random

from poker import Table


class Round:

    LOGGER = logging.getLogger(name="Round")

    def __init__(self, players, table_size, buy_in, min_denomination):
        self.players = players
        self.table_size = table_size
        self.buy_in = buy_in
        self.min_denomination = min_denomination

    def play(self):
        self.LOGGER.info("NEW ROUND")
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
        for _ in range(self.num_rounds):
            tournament_round = Round(self.players, self.table_size, self.buy_in, self.min_denomination)
            tournament_round.play()

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
        return difference
