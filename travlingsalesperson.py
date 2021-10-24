import pygame
import random

"""Genetic algorithm needs:
        *Representation of solution: List of the order in which the nodes are reached
        *Function for generating a population: List of solutions
        *Fitness function: Return total distance of the solution
        *Selection function: Select solutions to generate the next genaration
        *Cross over function: Takes in two parants and returns two children
        *Mutation function: Randomly mutates some solutions 
        
"""

class Node:
    def __init__(self, position):
        self.position = position

    def calc_dist(self, other):
        selfX,selfY = self.position
        otherX,otherY = other.position
        distX = (selfX-otherX)**2
        distY = (selfY-otherY)**2
        distance = (distX+distY)**0.5
        return distance

class Environment:
    def __init__(self,node_count,width,height):
        self.node_count = node_count
        self.width = width
        self.height = height
        self.node_list = []
        self.buildRandomWorld()

    def buildRandomWorld(self):
        self.node_list = [Node((random.randrange(self.width), random.randrange(self.height))) for i in range(self.node_count)]


class Population:
    def __init__(self, population_size,environment):
        self.population_size = population_size
        self.environment = environment
        self.population_list = [Solution(environment) for i in range(self.population_size)]
    
    def select_fittest(self, fitest_count = 4):
        self.population_list.sort(key=lambda solution: solution.fitness)
        return self.population_list[:fitest_count]

    def breed_new_solutions(self,fittest,target_count):
        child_nodes_list = []
        while len(child_nodes_list) < target_count:
            parentA = random.choice(fittest)
            parentB = random.choice([solution for solution in self.population_list if solution != parentA])
            child_nodes_list.append(Solution(self.environment,self.crossover(parentA,parentB)))
        return child_nodes_list

    def crossover(self,solutionA,solutionB):
        new_solution = []
        amount_of_solutionA_element = random.randrange(1,len(solutionA.solution))
        random_elements_from_A = random.sample(solutionA.solution, amount_of_solutionA_element)
        indexes_from_A = [list.index(solutionA.solution,node) for node in random_elements_from_A]
        while len(new_solution) < self.environment.node_count:
            if len(new_solution) in indexes_from_A:
                new_solution.append(solutionA.solution[len(new_solution)])
            else:
                for node in solutionB.solution:
                    if node not in random_elements_from_A and node not in new_solution:
                        new_solution.append(node)
                        break
        return new_solution

    def mutate(self, mutation_chance):
        for solution in self.population_list:
            if random.random() < mutation_chance:
                amount_of_elements_to_swap = random.randrange(1,len(solution.solution)//3)
                random_swap_elements = random.sample(solution.solution, amount_of_elements_to_swap)
                while random_swap_elements:
                    element = random_swap_elements[0]
                    new_index = random.randrange(len(solution.solution))
                    if new_index != list.index(solution.solution, element):
                        solution.solution[new_index],solution.solution[list.index(solution.solution, element)] = solution.solution[list.index(solution.solution, element)],solution.solution[new_index]
                        random_swap_elements.pop(0)
            

                


class Solution:
    def __init__(self,environment, solution_list = None):
        self.environment = environment
        self.solution = environment.node_list.copy() if not solution_list else solution_list
        self.fitness = self.fitness_function()
        if not solution_list:
            random.shuffle(self.solution)

    def fitness_function(self):
        cost = 0
        for node_index in range(len(self.solution)-1):
            cost += self.solution[node_index].calc_dist(self.solution[node_index + 1])
        cost += self.solution[-1].calc_dist(self.solution[0])
        return cost

    def draw(self,window):
        print(self)
        window.fill((0,0,0))
        for node in self.solution:
            pygame.draw.circle(window,(255,255,255),node.position, 6)
        for node_index in range(len(self.solution) - 1):
            pygame.draw.line(window,(255,0,0),self.solution[node_index].position,self.solution[node_index+1].position,4)
        pygame.draw.line(window,(255,0,0),self.solution[-1].position,self.solution[0].position,4)
        pygame.display.update()

def main():
    screen_width = 800
    screen_height = 800
    node_count = 25
    population_size = 20
    mutation_rate = 0.2
    env = Environment(node_count,screen_width,screen_height)
    window = pygame.display.set_mode((screen_width,screen_height))
    pygame.display.set_caption("Genetic TSP")
    population = Population(population_size,env)
    running = True
    FPS = 120
    clock = pygame.time.Clock()

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        fitest_solutions = population.select_fittest(10)
        l = [i.fitness for i in population.population_list]
        fitest_solutions[0].draw(window)
        print(fitest_solutions[0].fitness,l.count(fitest_solutions[0].fitness))
        offspring_count = population_size - len(fitest_solutions)
        offsprings = population.breed_new_solutions(fitest_solutions,offspring_count)
        next_generation = fitest_solutions + offsprings
        population.population_list = next_generation
        population.mutate(mutation_rate)
    pygame.quit()

    

if __name__ == "__main__":
    main()