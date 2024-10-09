from globals import *
import pygame
import numpy as np

class Quadtree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary
        self.capacity = capacity
        self.particles = []
        self.divided = False

        if showBorders: pygame.draw.rect(window, (0, 255, 0), boundary, 1)

    def subdivide(self):
        x, y, w, h = self.boundary
        nw = Quadtree((x, y, w/2, h/2), self.capacity)
        ne = Quadtree((x + w/2, y, w/2, h/2), self.capacity)
        sw = Quadtree((x, y + h/2, w/2, h/2), self.capacity)
        se = Quadtree((x + w/2, y + h/2, w/2, h/2), self.capacity)
        self.children = (nw, ne, sw, se)
        self.divided = True

    def insert(self, particle):
        if not self.boundaryContains(particle): return False

        if len(self.particles) < self.capacity:
            self.particles.append(particle)
            return True
        else:
            if not self.divided: self.subdivide()
            for child in self.children:
                if child.insert(particle): return True

    def query(self, treeRange, foundParticles):
        if not self.boundaryIntersects(treeRange): return
        for particle in self.particles:
            if np.linalg.norm([particle[0] - treeRange[0], particle[1] - treeRange[1]]) < particleDiameter:
                foundParticles.append(particle)
        if self.divided: [child.query(treeRange, foundParticles) for child in self.children]

    def boundaryContains(self, particle):
        x, y, w, h = self.boundary
        return (x <= particle[0] < x + w) and (y <= particle[1] < y + h)

    def boundaryIntersects(self, treeRange):
        x, y, w, h = self.boundary
        rx, ry, rw, rh = treeRange
        return (x < rx + rw) and (x + w > rx) and (y < ry + rh) and (y + h > ry)