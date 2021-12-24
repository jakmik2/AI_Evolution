from Organism import *

import numpy as np
import random
import os
import ctypes

from timeit import default_timer as timer


class Resources:
    def __init__(self, grid, amt=10):
        self.resources_available = amt  # This should be examined
        self.position = randomPosition(grid)

    def newYear(self):
        self.resources_available = random.randint(5, 15)


class Grid:
    def __init__(self, grid):
        self.grid = grid
        self.dim = len(grid[0])
        self.dictTracker = {}

    def add_object_to_grid(self, newObject):
        # Find position and replace 0 with the organism object
        self.dictTracker[newObject] = [newObject.position[0], newObject.position[1]]
        self.drawFromDict(newObject)

    def drawFromDict(self, object, empty=False):
        if empty:
            print(f"Old Coordinates {self.dictTracker[object]}")
            self.grid[self.dictTracker[object][0]][self.dictTracker[object][1]] = 0
        else:
            print(f"New Coordinates {self.dictTracker[object]}")
            self.grid[self.dictTracker[object][0]][self.dictTracker[object][1]] = object

    def UpdatePosition(self, object, newCoordinates):
        # Put 0 in Old Coordinates
        self.drawFromDict(object, empty=True)
        self.dictTracker[object] = newCoordinates
        self.drawFromDict(object)

    def printGrid(self):
        print(gridToString(self.grid))


class Env:
    def __init__(self, gridN, numStartingOrgs=0, nRes=None):
        self.dim = gridN
        self.grid = Grid([[0 for x in range(gridN)] for y in range(gridN)])
        self.Organisms = []
        for i in range(numStartingOrgs):
            self.addOrganism(Organism(first_gen=True, Env=self))

        self.resourceSpawns = []
        if nRes is None:
            tempAmt = gridN // 5
        else:
            tempAmt = nRes

        for i in range(tempAmt):
            self.addResourceSpawn(Resources(self.grid.grid, tempAmt))  # This is a fucking mess

    def addOrganism(self, newOrg):
        self.grid.add_object_to_grid(newOrg)
        self.Organisms += [newOrg]

    def addResourceSpawn(self, resourceSpawn):
        self.resourceSpawns += [resourceSpawn]
        self.grid.add_object_to_grid(resourceSpawn)

    def tickEnv(self):
        [n.decide(self.grid) for n in self.Organisms]
        self.grid.printGrid()


if __name__ == '__main__':
    Ecosystem = Env(25, 100)
    # find living org
    Ecosystem.grid.printGrid()
    for i in range(10):  # ten turns
        Ecosystem.tickEnv()
