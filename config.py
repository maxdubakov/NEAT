c1 = 1.0
c2 = 1.0
c3 = 0.4


""" THRESHOLDS """
sigma_threshold = 3.0
min_no_for_large_species = 5
fitness_stagnation_threshold = 15


""" MUTATION CHANCES """
weights_mutation = 0.8
weight_uniformly_perturbed = 0.9
random_weight = 0.1
gauss_mu = 0
gauss_sigma = 0.05


disable_connection_chance = 0.75
mutations_without_crossover = 0.25
interspecies_mating_rate = 0.001

mutated_part = 0.25  # crossover part is always { 1 - mutated_part }

new_node_rate = 0.03
new_link_rate = 0.05
new_link_rate_large_species = 0.3


population_size = 150


number_of_generations = 100

number_input_neurons = 2
number_output_neurons = 1
