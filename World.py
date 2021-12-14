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


class Env:
    def __init__(self, gridN, numStartingOrgs=0, nRes=None):
        self.dim = gridN
        self.grid = np.array([[0 for x in range(gridN)] for y in range(gridN)])
        self.Organisms = []
        for i in range(numStartingOrgs):
            self.addOrganism(Organism(first_gen=True, Grid=self.grid))

        self.resourceSpawns = []
        if nRes is None:
            tempAmt = gridN // 5
        else:
            tempAmt = nRes

        for i in range(tempAmt):
            self.addResourceSpawn(Resources(self.grid))

    def updateGrid(self, resourceBool=True):
        # Check all organisms positions and draw them
        self.grid = np.array([[0 for x in range(self.dim)] for y in range(self.dim)])
        if resourceBool:
            for resource in self.resourceSpawns:
                self.grid[resource.position[0]][resource.position[1]] = 1

        for org in self.Organisms:
            if org.alive:
                unit = 101
            else:
                unit = -1
            self.grid[org.position[0]][org.position[1]] = unit

    def printGrid(self):
        self.updateGrid()
        out_string = ''
        for y_array in self.grid:
            out_string += ''.join([str(x_elem) + ' ' * (5 - len(str(x_elem))) for x_elem in y_array])
            out_string += '\n'
        print(out_string)

    def addOrganism(self, newOrg):
        self.Organisms += [newOrg]

    def addResourceSpawn(self, resourceSpawn):
        self.resourceSpawns += [resourceSpawn]

    def tickEnv(self):
        [n.decide(self.grid) for n in self.Organisms]
        self.printGrid()


if __name__ == '__main__':
    Ecosystem = Env(25, 100)
    # find living org
    Ecosystem.printGrid()
    for i in range(10): # ten turns
        Ecosystem.tickEnv()
