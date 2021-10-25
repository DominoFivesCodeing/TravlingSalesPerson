import random
import pygame
import colorsys
import sys
import copy
from time import sleep

from pygame.locals import QUIT

class Node():
	def __init__(self, position):
		self.position = position

	def distance(self, other):
		x_dist = (self.position[0] - other.position[0]) ** 2
		y_dist = (self.position[1] - other.position[1]) ** 2
		distance = (x_dist + y_dist) ** 0.5
		return distance

class Environment():
	def __init__(self, node_count, width, height):
		self.node_count = node_count
		self.width = width
		self.height = height
		self.node_list = []

		self.build_random()
		#self.build_square(5, 3)

	def build_random(self):
		self.node_list = [Node((random.randrange(self.width), random.randrange(self.height))) for i in range(self.node_count)] # Create a list of random nodes

	def build_square(self, rect_width, rect_height):
		for x in range(rect_width):
			for y in range(rect_height):
				node_x = 25 + x * ((self.width / rect_width) - 10)
				node_y = 25 + y * ((self.height / rect_height) - 10)
				self.node_list.append(Node((int(node_x), int(node_y))))

class Individual():
	def __init__(self, environment):
		self.environment = environment
		self.solution = environment.node_list[:]
		random.shuffle(self.solution)

		self.cost = 0
		self.calculate_cost()
		self.opacity = 255
		self.line_color = self.random_line_color()

	def random_line_color(self):
		line_color_hsv = (random.randrange(255), 100, 200)
		rgb_tuple = hsv2rgb(line_color_hsv[0], line_color_hsv[1], line_color_hsv[2])
		line_color_rgb = (rgb_tuple[0], rgb_tuple[1], rgb_tuple[2], self.opacity)
		return line_color_rgb

	def randomize_line_color(self):
		self.line_color = self.random_line_color()

	# Total path weight (negative reward)
	def calculate_cost(self):
		cost = 0
		for i in range(len(self.solution) - 1):
			cost += self.solution[i].distance(self.solution[i+1]) # Distance between node i and i+1

		cost += self.solution[-1].distance(self.solution[0]) # First and last node
		self.cost = cost

	# True if both invididuals "self" and "other" have a solution that contains the same edge (specified by two nodes)
	# TODO: SHOULD CHECK IF ANY INDIV HAS AN EDGE, NOT BOTH.
	def has_edge(self, node_A, node_B):
		node_A_index = self.solution.index(node_A) # Index of node A in self
		node_B_index = self.solution.index(node_B) # Index of node B in self

		# There is a defined edge between node A and node B 
		return (node_A_index - 1 is node_B_index) or (node_A_index + 1 is node_B_index)

	def mutate(self, iterations):
		solution_len = len(self.solution)
		for i in range(iterations):
			index_a = random.randrange(solution_len)
			index_b = random.randrange(solution_len)
			self.solution[index_a], self.solution[index_b] = self.solution[index_b], self.solution[index_a] # Swap node orders

	def possible_crossover_nodes(source_node, individual_A, individual_B, available_nodes):
		crossover_node_list = []
		for target_node in available_nodes:
			if individual_A.has_edge(source_node, target_node) or individual_B.has_edge(source_node, target_node):
				crossover_node_list.append(target_node)

		return crossover_node_list

	# Redo???
	def crossover(self, other):
		start_gene = random.randrange(len(self.solution))
		end_gene = random.randrange(start_gene, len(self.solution))

		offspring_self_solution = [] # Offspring solution consisting of DNA from individual 'self'
		offspring_other_solution = [] # Offspring solution consisting of DNA from individual 'other'

		for i in range(start_gene, end_gene):
			offspring_self_solution.append(self.solution[i])

		offspring_other_solution = [item for item in other.solution if item not in offspring_self_solution] # Fill with "nucleotides" that don't already exist

		offspring = copy.deepcopy(self) # Let's say that "self" has some kind of dominant line-color gene or something lmao
		offspring.solution = offspring_self_solution + offspring_other_solution

		return offspring

class Population():
	def __init__(self, population_size, environment):
		self.population_size = population_size
		self.environment = environment

		self.population_list = [Individual(environment) for i in range(self.population_size)]

	def mutate(self, chance, iterations=1):
		for individual in self.population_list:
			if random.random() < chance:
				individual.mutate(iterations)

	def select_fittest(self, count=4):
		sorted_population = sorted(self.population_list, key=lambda obj: obj.cost)
		return sorted_population[:count]

	def breed(self, fittest, target_count):
		offspring_list = []
		print("Len fittest: ", len(fittest))
		while len(offspring_list) < target_count:
			for i in fittest:
				for j in fittest:
					if not (i is j):
						offspring = i.crossover(j)
						#offspring.randomize_line_color()
						offspring_list.append(offspring)
		return offspring_list

def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h/255,s/255,v/255))

def main():
	WIDTH = 1000
	HEIGHT = 500
	NODE_COUNT = 25
	POPULATION_SIZE = 1500
	MUTATION_CHANCE = 0.4

	environment = Environment(NODE_COUNT, WIDTH, HEIGHT)
	nodes = environment.node_list

	population = Population(POPULATION_SIZE, environment)

	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

	# Game loop
	while True:
		surface.fill((0,0,0, 255))
		screen.blit(surface, (0,0))

		# SELECTION
		fittest = population.select_fittest(count=12)

		# CROSSOVER
		offspring_count = POPULATION_SIZE - len(fittest)
		offspring = population.breed(fittest, offspring_count)
		population.population_list = fittest[:] + offspring[:offspring_count]

		# MUTATION
		population.mutate(MUTATION_CHANCE, iterations=random.randrange(3))

		pop_list = population.population_list
		for i in range(len(pop_list)):
			# FITNESS
			pop_list[i].calculate_cost()

			print("Cost:", pop_list[i].cost)
			solution_nodes = pop_list[i].solution
			line_color = pop_list[i].line_color
			start_end_line_color = (255 - line_color[0], 255 - line_color[1], 255 - line_color[2])

			if i == pop_list.index(fittest[0]):
				for i in range(len(solution_nodes) - 1):
					pygame.draw.line(surface, line_color, solution_nodes[i].position, solution_nodes[i+1].position, 2)
				pygame.draw.line(surface, start_end_line_color, solution_nodes[-1].position, solution_nodes[0].position, 4)
		
		screen.blit(surface, (0,0))

		for node in nodes:
			circle_color = (255, 255, 255)
			pygame.draw.circle(screen, circle_color, node.position, 6)

		pygame.display.flip()
		#sleep(0.5)

		for event in pygame.event.get():
			if event.type == QUIT:
				sys.exit(0)


if __name__ == '__main__':
	main()
