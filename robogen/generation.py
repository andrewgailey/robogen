
import individual
import constants
import random

class Generation:
    """This defines a group of Individuals to be compared in effectiveness."""

    def __init__(self):
        self.population = []
        self.num = 0
        
    def populate(self):
        """Populates a new Generation with default Individuals."""
        
        for x in range(constants.pop_size):
            self.population.append(individual.Individual())
            
    def propagate(self):
        """Creates a new Generation through mutation and breeding."""
        
        new_gen = Generation()
        new_gen.num = self.num + 1
        self.sort_by_score()
        # Elites
        for x in range(constants.elite_size):
            self.population[x].gens_as_elite += 1
            new_gen.population.append(self.population[x])
        # Low Rate Mutations
        for x in range(constants.lo_mut_size):
            idx = Generation.half_gauss_range(len(self.population))
            clone = self.population[idx].do_mutations(constants.lo_muts_per_indiv)
            new_gen.population.append(clone)
        # High Rate Mutations
        for x in range(constants.hi_mut_size):
            idx = Generation.half_gauss_range(len(self.population))
            clone = self.population[idx].do_mutations(constants.hi_muts_per_indiv)
            new_gen.population.append(clone)
        # Cross Breeding
        for x in range(constants.cross_size):
            idx1 = Generation.half_gauss_range(len(self.population))
            idx2 = idx1
            while idx2 == idx1:
                idx2 = Generation.half_gauss_range(len(self.population))
            offspring = individual.Individual.cross(
                            self.population[idx1], self.population[idx2])
            new_gen.population.append(offspring)
        return new_gen
        
    # def print_scores(self):
        # str = ""
        # for indiv in self.population:
            # str = str + " : {0}".format(indiv.score)
        # print "Scores" + str
        
    def sort_by_score(self):
        """Sort Individuals from high score to low score."""
        
        self.population.sort()
        self.population.reverse()
                
    @staticmethod
    def half_gauss_range(range):
        """Choose a number in the given range, heavily favoring low numbers"""
        
        result = int(abs(random.gauss(0, (range/2.0))))
        if result >= range:
            result = 0
        return result
        
    def debug_print(self):
        print "Generation:", self.num
        for indiv in self.population:
            indiv.debug_print()
            