from config import max_no_of_generations_fitness_not_growing as max_size

class Species:

    def __init__(self, _id):
        self._id = _id
        self._representatives = list()
        self._fitnesses = list()


    def adjusted_fitness(self):
        sum_adjusted_fitness = 0
        for org in self._representatives:
            sum_adjusted_fitness += org.score()
        return sum_adjusted_fitness/len(self._representatives)


    def representatives(self):
        return self._representatives

    def size(self):
        return len(self._representatives)

    def append_fitness(self, fitness):
        if len(self._fitnesses) == max_size:
            del self._fitnesses[0]
        self._fitnesses.append(fitness)

    def __str__(self):
        return f'Species ({self._id})'
