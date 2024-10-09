import pygame

width, height = 1920, 1010

window = pygame.display.set_mode((1800, 900), pygame.RESIZABLE, pygame.FULLSCREEN)
clock = pygame.time.Clock()

particleRadius = 3
particleDiameter = particleRadius * 2
numParticles = 600
particleRadius = 3

quadtreeCapacity = 1 # reduce for optimal performance
entropy = 0.1

showBorders = True
