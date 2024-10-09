from globals import *
import pygame
import numpy as np
from random import uniform
from Quadtree import Quadtree, window

pygame.init()

numParticles = 600
particleRadius = 5

font = pygame.font.Font(size=35)

def renderFPS(display): display.blit(font.render(f'FPS: {round(clock.get_fps(), 2)}', True, (255, 255, 255)), (0, 0))

def resolveCollision(p1, p2):
    p1x, p1y, p2x, p2y = p1[0], p1[1], p2[0], p2[1]
    angle = np.arctan2(p2y - p1y, p2x - p1x)
    overlap = ((particleRadius<<1) - np.linalg.norm([p2x-p1x, p2y-p1y]))/2
    Osin, Ocos, = np.sin(angle)*overlap, np.cos(angle)*overlap
    p1[0] -= Ocos
    p1[1] -= Osin
    p2[0] -= Ocos
    p2[1] -= Osin

def main() -> None:

    showBorders = True
   
    particles = np.array([np.array((uniform(0, width), uniform(0, height), 0, 0), dtype=float) for _ in range(numParticles)], dtype=list) #[x, y, vx, vy]

    quadtree = Quadtree((0, 0, width, height), quadtreeCapacity)

    [quadtree.insert(particle) for particle in particles]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(), exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    showBorders = not showBorders
                    print('dsa')


        for particle in particles:
            particle[2] += uniform(-entropy, entropy)
            particle[3] += uniform(-entropy, entropy)
            
            particle[0], particle[1] = (particle[0] + particle[2]) % width, (particle[1] + particle[3]) % height

        window.fill((0, 0, 0))

        for particle in particles:
            p0, p1 = particle[0], particle[1]
            treeRange = (p0, p1, particleRadius<<1, particleRadius<<1)
            foundParticles = []
            quadtree.query(treeRange, foundParticles)
            for otherParticle in foundParticles:
                if not np.array_equal(particle, otherParticle):
                    if np.linalg.norm((p0 - otherParticle[0], p1 - otherParticle[1])) < (particleRadius<<1): 
                        resolveCollision(particle, otherParticle)

        # Update quadtree with particle positions
        quadtree = Quadtree((0, 0, width, height), quadtreeCapacity)

        [(quadtree.insert(particle), pygame.draw.circle(window, (200, 200, 200), (int(particle[0]), int(particle[1])), particleRadius))
        for particle in particles]

        renderFPS(window)
        pygame.display.update()
        clock.tick(100)

if __name__ == '__main__':
    main()