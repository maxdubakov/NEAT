import copy
import random
import math

from config import population_size, sigma_threshold, fitness_stagnation_threshold, \
    mutated_part, interspecies_mating_rate, number_input_neurons, number_output_neurons
from genome.Genome import Genome
from nn.NeuralNetwork import NeuralNetwork
from generation.Species import Species
import generation.util.Genomes as gens
from generation.util.Genomes import produce_offspring
from util.ranges import within_range
from visual.net import construct

# TODO: 50% of generation can die off

class Generation:

    INIT_ID = 0

    def __init__(self, prev_generation=None):
        self._organisms = list()
        self._species = list()
        self._representative_of_species = dict()

        if prev_generation is None:
            self._initialized_first_genome = False
            self._innovation_number = 1
            self._node_id = 1
            self._species_number = 1
            self._mutations = list()
            self._nodes = list()
            self._id = Generation.INIT_ID
        else:
            self._initialized_first_genome = prev_generation.has_first_genome()
            self._innovation_number = prev_generation.innovation_number()
            self._node_id = prev_generation.node_id()
            self._species_number = prev_generation.species_number()
            self._mutations = copy.deepcopy(prev_generation.mutations())
            self._nodes = copy.deepcopy(prev_generation.nodes())
            self._id = prev_generation.id() + 1


    def spawn(self):
        for i in range(population_size):
            genome = Genome(self, number_input_neurons, number_output_neurons)
            nn = NeuralNetwork(genome)
            self.add_organism(nn)


    def evaluate(self, solve_task, reward_function, **kwargs):
        for org in self._organisms:
            predictions = org.simulate(solve_task, **kwargs)
            if predictions is None:
                self._organisms.remove(org)
                for s in self._species:
                    if org in s.representatives():
                        s.representatives().remove(org)
                        break
            else:
                org.set_score(reward_function(predictions, kwargs['y_train']))


    def speciation(self):
        for org in self._organisms:
            assigned = False
            for species, rep in self._representative_of_species.items():
                if gens.sigma(org.genome(), rep.genome()) < sigma_threshold:
                    self._species[self._species.index(species)].add_representative(org)
                    org.assign_to_species(species)
                    assigned = True
                    break

            if not assigned:
                species = Species(self._species_number)
                species.add_representative(org)
                org.assign_to_species(species)
                self.add_species(species)
                self.add_representative_of_species(species, org)
                self._species_number += 1


    def eliminate(self):
        for species in self._species:
            if len(species.representatives()) > 1:
                to_eliminate = species.representatives()[0]
                for rep in species.representatives():
                    if rep.score() < to_eliminate.score():
                        to_eliminate = rep

                self._organisms.remove(to_eliminate)
                species.representatives().remove(to_eliminate)


    def reproduce(self, avg_ad_fitness):

        for species in self._species:
            if species.max_unchanged_for() == fitness_stagnation_threshold:
                print('Eliminating in reproduce: stagnation()')
                self._delete_species(species)

            if species.empty():
                print('Eliminating in reproduce: species.empty()')
                self._delete_species(species)

        new_generation = Generation(prev_generation=self)

        for species in self._species:
            new_size = math.ceil(species.get_new_size(avg_ad_fitness))
            no_of_orgs_mutated = math.ceil(new_size * mutated_part)
            no_of_crossover = new_size - no_of_orgs_mutated
            if new_size == 0:
                print('Eliminating in reproduce: new_size == 0')
                self._delete_species(species)
            else:
                champion = species.get_champion()
                if champion is not None:
                    champion.new_generation(new_generation)
                    new_generation.add_organism(champion)

                for i in random.choices(range(len(species.representatives())), k=no_of_orgs_mutated):
                    species.representatives()[i].mutate()
                    species.representatives()[i].new_generation(new_generation)
                    new_generation.add_organism(species.representatives()[i])

                for i, j in zip(random.choices(range(len(species.representatives())), k=no_of_crossover),
                                random.choices(range(len(species.representatives())), k=no_of_crossover)):
                    if not within_range(interspecies_mating_rate):
                        offspring = NeuralNetwork(produce_offspring(new_generation,
                                                  species.representatives()[i].genome(),
                                                  species.representatives()[j].genome()))
                    else:
                        rep_of_random_species = random.choice(self._organisms)
                        offspring = NeuralNetwork(produce_offspring(new_generation,
                                                                    rep_of_random_species.genome(),
                                                                    species.representatives()[j].genome()))
                    new_generation.add_organism(offspring)

                random_rep = random.choice(species.representatives())
                new_generation.add_species(species.empty_species())
                new_generation.add_representative_of_species(species, random_rep)
        return new_generation


    def step(self, solve_task, reward_function, **kwargs):
        # TODO: figure out where do they mutate
        if self._id == Generation.INIT_ID:
            self.spawn()
        self.evaluate(solve_task, reward_function, **kwargs)
        self.speciation()
        self.eliminate()
        self._eliminate_empty_species()
        avg_ad_fitness = self.ad_fitness()
        return avg_ad_fitness


    """ HELPERS """
    def get_innovation_number(self, connection):
        for mutation in self._mutations:
            if mutation == connection:
                return mutation.innovation_number()

        self.increase()
        return self._innovation_number - 1

    def _eliminate_empty_species(self):
        for s in self._species:
            if s.empty():
                print('Eliminating in _eliminate_empty_species')
                self._delete_species(s)

    def _delete_species(self, species):
        for rep in species.representatives():
            self._organisms.remove(rep)
            species.representatives().remove(rep)
        self._species.remove(species)
        print(f'{species} extincted')

    def innovation_number(self):
        return self._innovation_number

    def node_id(self):
        return self._node_id

    def increase_node_id(self):
        self._node_id += 1

    def increase(self, times=1):
        self._innovation_number += times

    def mutations(self):
        return self._mutations


    def put_mutation(self, mutation):
        found = False
        for mut in self._mutations:
            if mutation == mut:
                found = True
                break
        if not found:
            self._mutations.append(mutation)


    def ad_fitness(self):
        avg_ad_fitness = 0
        for org in self._organisms:
            avg_ad_fitness += org.score()

        return avg_ad_fitness/len(self._organisms)


    def nodes(self):
        return self._nodes

    def has_first_genome(self):
        return self._initialized_first_genome

    def put_first_genome(self):
        self._initialized_first_genome = True

    def add_organism(self, organism):
        self._organisms.append(organism)

    def organisms(self):
        return self._organisms

    def species_number(self):
        return self._species_number

    def species(self):
        return self._species

    def id(self):
        return self._id

    def add_representative_of_species(self, species, rep):
        self._representative_of_species[species] = rep

    def add_species(self, species):
        self._species.append(species)

    def representative_of_species(self):
        return self._representative_of_species

    def __str__(self):
        return f'Generation({str(self._id)})'

    def full_info(self):
        organisms = '\nORGANISMS'
        for org in self._organisms:
            organisms += '\n' + str(org)
        organisms += f'\nlen: {len(self._organisms)}'

        species = '\n\nSPECIES'
        for s in self._species:
            species += '\n' + str(s) + ': ' + str(len(s.representatives()))

        return organisms + species

    def ready(self, score):
        for s in self._species:
            for rep in s.representatives():
                if rep.score() >= score:
                    return rep
        return None

    def info(self):
        species_score = ''
        for s in self._species:
            species_score += str(s) + '=' + str(round(s.adjusted_fitness(), 1)) + f'; size={len(s.representatives())}\n'
        return '\n\n\n' + '-'*20 + ' INFO ' + '-'*20 +\
               f'\nGeneration({self._id}) avg. score={round(self.ad_fitness(), 1)}; size={len(self._organisms)}' \
               f'\nSpecies:\n{species_score}' \
               + '-'*46 + '\n\n\n'


    def visualize_species(self):
        for s in self._species:
            if not s.empty():
                rep = random.choice(s.representatives())
                construct(rep.genome(), str(s), view=False)


    def folder_name(self):
        return f'generation_{self._id}'
