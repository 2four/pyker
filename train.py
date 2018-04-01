import _MultiNEAT as NEAT
from math import ceil, log2
from copy import deepcopy
import click
import logging

from tournament import Tournament, PlayOff

_action_vector_size = 3
_card_vector_size = 13 + 4
_red = "\x1b[31m"
_normal = "\x1b[0m"
_genome_store = "genome/{}-{}"


class Training:

    LOGGER = logging.getLogger(name="Training")

    def __init__(self, table_size, buy_in, min_denomination, tournament_rounds):
        self.table_size = table_size
        self.buy_in = buy_in
        self.min_denomination = min_denomination
        self.tournament_rounds = tournament_rounds

        self.set_card_vector_size()
        self.set_money_vector_size()
        self.set_action_vector_size()
        self.set_in_vector_size()

        self.neat_parameters = NEAT.Parameters()
        self.neat_parameters.DetectCompetetiveCoevolutionStagnation = True
        self.neat_parameters.MutateAddNeuronProb = 0.1
        self.neat_parameters.MutateAddLinkProb = 0.2
        self.neat_parameters.CompatTreshold = 0.5
        self.neat_parameters.DynamicCompatibility = True
        self.neat_parameters.CompatTresholdModifier = 0.005

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

    @staticmethod
    def get_best_n_genomes(population, n):
        num_genomes = population.NumGenomes()
        genomes = [population.AccessGenomeByIndex(genome_index) for genome_index in range(num_genomes)]
        genomes.sort(key=lambda genome: genome.GetFitness(), reverse=True)
        return [deepcopy(genome) for genome in genomes[:n]]

    def create_genome(self):
        genome = NEAT.Genome(
            0,
            self.in_vector_size,
            0,
            self.action_vector_size,
            True,
            NEAT.ActivationFunction.UNSIGNED_SIGMOID,
            NEAT.ActivationFunction.UNSIGNED_SIGMOID,
            0,
            self.neat_parameters,
            0
        )
        return genome

    def run(self):
        logging.basicConfig(
            format=_red + "[%(levelname)s][%(asctime)s][%(name)s] %(message)s" + _normal,
            datefmt="%m/%d/%Y %H:%M:%S",
            level=logging.WARN
        )

        genome = self.create_genome()
        population = NEAT.Population(genome, self.neat_parameters, True, 1.0, 0)
        previous_best_genomes = None
        current_best_genomes = None
        difference = 0

        self.LOGGER.warn("Population size: {}".format(population.NumGenomes()))

        self.LOGGER.warn("{:>14s} {:>14s} {:>14s} {:>14s} {:>14s} {:>14s}".format(
            "n_species",
            "stagnation",
            "mpc",
            "search_mode",
            "compat_thresh",
            "improvement"
        ))

        # run for 100 generations
        for generation in range(200):
            tournament = Tournament(
                population,
                self.table_size,
                self.money_vector_size,
                self.buy_in,
                self.min_denomination,
                self.tournament_rounds
            )

            tournament.play()

            if current_best_genomes:
                previous_best_genomes = current_best_genomes

            current_best_genomes = self.get_best_n_genomes(population, self.table_size // 2)

            if previous_best_genomes:
                playoff = PlayOff(
                    current_best_genomes,
                    previous_best_genomes,
                    self.table_size,
                    self.money_vector_size,
                    self.buy_in,
                    self.min_denomination,
                    self.tournament_rounds
                )
                difference += playoff.play()

            for index in range(population.NumGenomes()):
                genome = population.AccessGenomeByIndex(index)
                genome.SetFitness(genome.GetFitness() + difference)

            self.LOGGER.warn("{:14d} {:14d} {:14.2f} {:>14s} {:14.3f} {:14.2f}".format(
                len(population.Species),
                population.GetStagnation(),
                population.GetCurrentMPC(),
                population.GetSearchMode().name,
                population.Parameters.CompatTreshold,
                difference
            ))

            population.Epoch()

        self.LOGGER.warn("Training complete")
        return self.get_best_n_genomes(population, self.table_size)


def _save_genomes(genomes, genome_name):
    genome_indices = range(len(genomes))
    for index, genome in zip(genome_indices, genomes):
        save_name = _genome_store.format(genome_name, index)
        genome.Save(save_name)


@click.command()
@click.argument("genome_name", type=str)
@click.option("--table_size", default=8, help="Number of players round a table")
@click.option("--buy_in", default=8000, help="Number of chips each player starts with")
@click.option("--min_denomination", default=25, help="Minimum chip denomination")
@click.option("--tournament_rounds", default=10, help="Number of rounds per training tournament")
def main(genome_name, table_size=8, buy_in=8000, min_denomination=25, tournament_rounds=10):
    training = Training(table_size, buy_in, min_denomination, tournament_rounds)
    top_genomes = training.run()
    _save_genomes(top_genomes, genome_name)


if __name__  == "__main__":
    main()
