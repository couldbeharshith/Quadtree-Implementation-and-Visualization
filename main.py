from math import ceil, hypot
from random import uniform

import pygame

from globals import entropy, height, numParticles, particleDiameter, particleRadius, quadtreeCapacity, width
from Quadtree import Quadtree

canvasSize = (1440, 900)
arena = pygame.Rect(48, 96, 1344, 707)
maxSpeed = particleRadius

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
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    distance = hypot(dx, dy)
    if distance >= particleDiameter:
        return

    dvx, dvy = p1[2] - p2[2], p1[3] - p2[3]
    if distance:
        nx, ny = dx / distance, dy / distance
    else:
        relativeSpeed = hypot(dvx, dvy)
        nx, ny = (dvx / relativeSpeed, dvy / relativeSpeed) if relativeSpeed else (1, 0)

    shift = (particleDiameter - distance) / 2
    p1[0] -= shift * nx
    p1[1] -= shift * ny
    p2[0] += shift * nx
    p2[1] += shift * ny

    # Equal masses exchange their velocity components along the contact normal.
    closingSpeed = dvx * nx + dvy * ny
    if closingSpeed > 0:
        p1[2] -= closingSpeed * nx
        p1[3] -= closingSpeed * ny
        p2[2] += closingSpeed * nx
        p2[3] += closingSpeed * ny

    containParticle(p1)
    containParticle(p2)


def containParticle(particle):
    for axis, extent in enumerate((width, height)):
        if particle[axis] <= particleRadius:
            particle[axis] = particleRadius
            particle[axis + 2] = abs(particle[axis + 2])
        elif particle[axis] >= extent - particleRadius:
            particle[axis] = extent - particleRadius
            particle[axis + 2] = -abs(particle[axis + 2])


def buildTree(particles):
    quadtree = Quadtree((0, 0, width, height), quadtreeCapacity)
    for particle in particles:
        quadtree.insert(particle)
    return quadtree


def advanceParticles(particles):
    fastest = 0
    for particle in particles:
        particle[2] += uniform(-entropy, entropy)
        particle[3] += uniform(-entropy, entropy)
        speed = hypot(particle[2], particle[3])
        if speed > maxSpeed:
            scale = maxSpeed / speed
            particle[2] *= scale
            particle[3] *= scale
            speed = maxSpeed
        fastest = max(fastest, speed)

    # Keep movement small relative to a circle so fast particles still meet.
    substeps = max(1, ceil(fastest / (particleRadius / 2)))
    for _ in range(substeps):
        for particle in particles:
            particle[0] += particle[2] / substeps
            particle[1] += particle[3] / substeps
            containParticle(particle)

        quadtree = buildTree(particles)
        pairs = []
        visited = set()
        # Find pairs before the response moves particles out of their indexed cells.
        for particle in particles:
            visited.add(id(particle))
            x, y = particle[:2]
            foundParticles = []
            quadtree.query((x - particleDiameter, y - particleDiameter,
                            2 * particleDiameter, 2 * particleDiameter), foundParticles)
            pairs.extend((particle, other) for other in foundParticles if id(other) not in visited)

        for particle, other in pairs:
            resolveCollision(particle, other)


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

    particles = [[uniform(particleRadius, width - particleRadius),
                  uniform(particleRadius, height - particleRadius), 0.0, 0.0]
                 for _ in range(numParticles)]  # x, y, vx, vy

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

        advanceParticles(particles)
        quadtree = buildTree(particles) if showBorders else None
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
