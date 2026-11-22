import numpy as np
import pygame
from random import uniform

from globals import entropy, height, numParticles, quadtreeCapacity, width
from Quadtree import Quadtree

particleRadius = 5
canvasSize = (1440, 900)
arena = pygame.Rect(48, 96, 1344, 707)

background = (0, 0, 0)
border = (52, 52, 52)
muted = (158, 158, 158)
textColor = (232, 232, 232)


def render(canvas, simulation, quadtree, particles, showBorders, fps, fonts):
    titleFont, labelFont = fonts
    canvas.fill(background)
    title = titleFont.render('Quadtree', True, textColor)
    canvas.blit(title, (arena.left, 42))

    gridLabel = labelFont.render('W  Grid on' if showBorders else 'W  Grid off', True, muted)
    canvas.blit(gridLabel, gridLabel.get_rect(topright=(arena.right, 49)))

    simulation.fill(background)
    if showBorders:
        quadtree.draw(simulation)
    for x, y, _, _ in particles:
        pygame.draw.circle(simulation, textColor, (int(x), int(y)), particleRadius)
    pygame.transform.smoothscale(simulation, arena.size, canvas.subsurface(arena))
    pygame.draw.rect(canvas, border, arena.inflate(2, 2), 1)

    particleLabel = labelFont.render(f'{len(particles)} particles', True, muted)
    canvas.blit(particleLabel, (arena.left, 829))
    fpsLabel = labelFont.render(f'{fps:.0f} FPS', True, muted)
    canvas.blit(fpsLabel, fpsLabel.get_rect(topright=(arena.right, 829)))


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
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_caption('Quadtree Visualization')
    desktopWidth, desktopHeight = pygame.display.get_desktop_sizes()[0]
    windowScale = min(1, desktopWidth * 0.9 / canvasSize[0], desktopHeight * 0.88 / canvasSize[1])
    window = pygame.display.set_mode(tuple(round(size * windowScale) for size in canvasSize), pygame.RESIZABLE)
    canvas = pygame.Surface(canvasSize).convert()
    simulation = pygame.Surface((width, height)).convert()
    clock = pygame.time.Clock()
    fonts = (
        pygame.font.SysFont('dejavusans,arial', 30, bold=True),
        pygame.font.SysFont('dejavusans,arial', 16),
    )
    showBorders = True

    particles = [np.array((uniform(0, width), uniform(0, height), 0, 0), dtype=float)
                 for _ in range(numParticles)]  # x, y, vx, vy
    quadtree = Quadtree((0, 0, width, height), quadtreeCapacity)
    for particle in particles:
        quadtree.insert(particle)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if event.key == pygame.K_w:
                    showBorders = not showBorders

        for particle in particles:
            particle[2] += uniform(-entropy, entropy)
            particle[3] += uniform(-entropy, entropy)
            particle[0] = (particle[0] + particle[2]) % width
            particle[1] = (particle[1] + particle[3]) % height

        for particle in particles:
            x, y = particle[:2]
            treeRange = (x, y, particleRadius << 1, particleRadius << 1)
            foundParticles = []
            quadtree.query(treeRange, foundParticles)
            for otherParticle in foundParticles:
                if not np.array_equal(particle, otherParticle):
                    if np.linalg.norm((x - otherParticle[0], y - otherParticle[1])) < particleRadius << 1:
                        resolveCollision(particle, otherParticle)

        quadtree = Quadtree((0, 0, width, height), quadtreeCapacity)
        for particle in particles:
            quadtree.insert(particle)

        render(canvas, simulation, quadtree, particles, showBorders, clock.get_fps(), fonts)
        frame = canvas.get_rect().fit(window.get_rect())
        frame.center = window.get_rect().center
        window.fill(background)
        if frame.size == canvasSize:
            window.blit(canvas, frame)
        elif frame.width and frame.height:
            pygame.transform.smoothscale(canvas, frame.size, window.subsurface(frame))
        pygame.display.flip()
        clock.tick(100)


if __name__ == '__main__':
    main()
