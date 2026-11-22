import pygame

class Quadtree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary
        self.capacity = capacity
        self.particles = []
        self.divided = False

    def draw(self, surface, depth=0):
        if not self.divided:
            return
        x, y, w, h = self.boundary
        midX, midY = x + w / 2, y + h / 2
        shade = max(52, 104 - depth * 13)
        color = (shade, shade, shade)
        pygame.draw.line(surface, color, (midX, y), (midX, y + h), 2)
        pygame.draw.line(surface, color, (x, midY), (x + w, midY), 2)
        for child in self.children:
            child.draw(surface, depth + 1)

    def subdivide(self):
        x, y, w, h = self.boundary
        self.midX, self.midY = x + w/2, y + h/2
        nw = Quadtree((x, y, w/2, h/2), self.capacity)
        ne = Quadtree((self.midX, y, w/2, h/2), self.capacity)
        sw = Quadtree((x, self.midY, w/2, h/2), self.capacity)
        se = Quadtree((self.midX, self.midY, w/2, h/2), self.capacity)
        self.children = (nw, ne, sw, se)
        self.divided = True

    def insert(self, particle):
        if not self.boundaryContains(particle):
            return False

        node = self
        while len(node.particles) >= node.capacity and min(node.boundary[2:]) > 1:
            if not node.divided:
                node.subdivide()
            east = particle[0] >= node.midX
            south = particle[1] >= node.midY
            node = node.children[2 * south + east]

        # A cell at the minimum size can hold multiple coincident particles.
        node.particles.append(particle)
        return True

    def query(self, treeRange, foundParticles):
        if not self.boundaryIntersects(treeRange): return
        x, y, w, h = treeRange
        right, bottom = x + w, y + h
        for particle in self.particles:
            if x <= particle[0] < right and y <= particle[1] < bottom:
                foundParticles.append(particle)
        if self.divided:
            for child in self.children:
                child.query(treeRange, foundParticles)

    def boundaryContains(self, particle):
        x, y, w, h = self.boundary
        return (x <= particle[0] < x + w) and (y <= particle[1] < y + h)

    def boundaryIntersects(self, treeRange):
        x, y, w, h = self.boundary
        rx, ry, rw, rh = treeRange
        return (x < rx + rw) and (x + w > rx) and (y < ry + rh) and (y + h > ry)
