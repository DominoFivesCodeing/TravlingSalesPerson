import pygame
import random
import copy

"""Genetic algorithm needs:
        *Representation of solution: List of the order in which the nodes are reached
        *Function for generating a population: List of solutions
        *Fitness function: Return total distance of the solution
        *Selection function: Select solutions to generate the next genaration
        *Cross over function: Takes in two parants and returns two children
        *Mutation function: Randomly mutates some solutions 
        
"""

class Node:
    def __init__(self, position, ID):
        self.position = position
        self.ID = ID

    def __repr__(self):
        return str(self.ID)

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
        self.node_list = [Node((random.randrange(self.width), random.randrange(self.height)),i) for i in range(self.node_count)]

    def print_matrix(self):
        matrix = []
        for i in self.node_list:
            matrix_row = [i, []]
            for n in self.node_list:
                if i != n:
                    matrix_row[1].append((n,i.calc_dist(n)))
            matrix.append(matrix_row)
        for i in matrix:
            print(i)
            print("\n")


class Population:
    def __init__(self, population_size,environment):
        self.population_size = population_size
        self.environment = environment
        self.population_list = [Candidate(environment,environment.node_list,True) for i in range(self.population_size)]
    
    def select_fittest(self, fitest_count = 4):
        self.population_list.sort(key=lambda solution: solution.cost)
        return self.population_list[:fitest_count]

    def select_parents(self, parents_amount = 2):
        candidates = []
        population = self.population_list
        while(len(candidates) < parents_amount):
            candidate_A, candidate_B = tuple(random.sample(population,2))
            if candidate_A not in candidates and candidate_B not in candidates:
                strongest_candidate = candidate_A if candidate_A.cost < candidate_B.cost else candidate_B
                candidates.append(strongest_candidate)
        return candidates

    def breed_new_solutions(self,parents,target_count):
        next_gneration_children = []
        while len(next_gneration_children) < target_count:
            parentA = random.choice(parents)
            parentB = random.choice([solution for solution in self.population_list if solution != parentA])
            next_gneration_children.append(self.crossover(parentA,parentB))
        return next_gneration_children

    def crossover(self,parent_A,parent_B):
        inheritance_A = []
        inheritance_B = []
        start_gene = random.randrange(len(parent_A.solution))
        end_gene = random.randrange(start_gene ,len(parent_A.solution))
        for i in range(start_gene, end_gene):
            inheritance_A.append(parent_A.solution[i])
        inheritance_B = [item for item in parent_B.solution if item not in inheritance_A]
        return Candidate(self.environment, inheritance_A + inheritance_B) 

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
            

                


class Candidate:
    def __init__(self,environment, solution_list, shuffleSolution = False):
        self.environment = environment
        self.solution = solution_list
        if shuffleSolution:
            random.shuffle(self.solution)
        self.cost = self.fitness_function()
            

    def __repr__(self):
        return str(self.cost)

    def fitness_function(self):
        cost = 0
        for node_index in range(len(self.solution)-1):
            cost += self.solution[node_index].calc_dist(self.solution[node_index + 1])
        cost += self.solution[-1].calc_dist(self.solution[0])
        return cost

    def draw(self,window):
        window.fill((0,0,0))
        pygame.draw.circle(window,(0,255,0),self.solution[0].position, 6)
        for node in self.solution[1:]:
            pygame.draw.circle(window,(255,255,255),node.position, 6)
        for node_index in range(len(self.solution) - 1):
            pygame.draw.line(window,(255,0,0),self.solution[node_index].position,self.solution[node_index+1].position,4)
        pygame.draw.line(window,(255,0,0),self.solution[-1].position,self.solution[0].position,4)
        pygame.display.update()

def main():
    screen_width = 800
    screen_height = 800
    node_count = 25
    population_size = 30
    mutation_rate = 0.15
    env = Environment(node_count,screen_width,screen_height)
    window = pygame.display.set_mode((screen_width,screen_height))
    pygame.display.set_caption("Genetic TSP")
    population = Population(population_size,env)
    running = True
    FPS = 300
    clock = pygame.time.Clock()
    iterations_limit = 500
    iteration_counter = 0
    position_list = []
    for i in env.node_list:
        position_list.append(i.position)

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if iteration_counter < iterations_limit:
            best_candidates = population.select_fittest()
            parents = population.select_parents(4)
            best_candidates[0].draw(window)
            offspring_count = population_size - len(best_candidates)
            offsprings = population.breed_new_solutions(parents,offspring_count)
            next_generation = best_candidates + offsprings
            population.population_list = next_generation
            population.mutate(mutation_rate)
            print(best_candidates[0].solution)
            print("Iteration: " + str(iteration_counter), "Lowest score: " + str(best_candidates[0]))
            iteration_counter += 1
    env.print_matrix()
    pygame.quit()

    

if __name__ == "__main__":
    main()