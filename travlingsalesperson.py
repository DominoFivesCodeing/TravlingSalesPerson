import pygame
import random

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

    def draw(self,window,):
        window.fill((0,0,0))
        for node in self.node_list:
            pygame.draw.circle(window,(255,255,255),node.position, 6)
        for node in self.node_list:
            for other in self.node_list:
                if node != other:
                    pygame.draw.line(window,(255,0,0),node.position,other.position,4)
        pygame.display.update()


    def buildRandomWorld(self):
        self.node_list = [Node((random.randrange(self.width), random.randrange(self.height))) for i in range(self.node_count)]



def main():
    screen_width = 800
    screen_height = 800
    node_count = 8
    env = Environment(node_count,screen_width,screen_height)
    window = pygame.display.set_mode((screen_width,screen_height))
    surface = pygame.Surface((screen_width,screen_height))
    pygame.display.set_caption("Genetic TSP")
    for n in env.node_list:
        print(n.position)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        env.draw(window)
    pygame.quit()

    

if __name__ == "__main__":
    main()