from Organism import *

import numpy as np
import random
import os
import ctypes

from timeit import default_timer as timer

# Globals
counter = 10000
current_year = 0


class Resources:
    def __init__(self, grid, amt=10):
        self.resources_available = amt  # This should be examined
        self.position = randomPosition(grid)


class Env:
    def __init__(self, gridN, numStartingOrgs=0, nRes=None):
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

    def updateGrid(self, resBool=False):
        # Check all organisms positions and draw them
        if resBool:
            for resource in self.resourceSpawns:
                self.grid[resource.position[0]][resource.position[1]] = 1
        else:
            for org in self.Organisms:
                if org.alive:
                    unit = org.id
                else:
                    unit = (-1)
                self.grid[org.position[0]][org.position[1]] = unit

    def printGrid(self):
        out_string = ''
        for y_array in self.grid:
            out_string += ''.join([str(x_elem) + ' ' * (7 - len(str(x_elem))) for x_elem in y_array])
            out_string += '\n'
        print(out_string)

    def addOrganism(self, newOrg):
        self.Organisms += [newOrg]
        self.updateGrid()

    def addResourceSpawn(self, resourceSpawn):
        self.resourceSpawns += [resourceSpawn]
        self.updateGrid(resBool=True)


def localSight(Grid):
    position = [10, 10]
    print()# grid of what can be seen



if __name__ == '__main__':
    Ecosystem = Env(25, 100)

    Ecosystem.printGrid()

    localSight(Ecosystem.grid)

