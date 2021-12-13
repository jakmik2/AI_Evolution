from Organism import *

import numpy as np
import random
import os

from timeit import default_timer as timer

# Globals
counter = 10000
current_year = 0


class Env:
    def __init__(self, gridN, numStartingOrgs=0):
        self.grid = np.array([[0 for x in range(gridN)] for y in range(gridN)])
        self.Organisms = []
        for i in range(numStartingOrgs):
            self.addOrganism(Organism(first_gen=True, Grid=self.grid))

    def updateGrid(self):
        # Check all organisms positions and draw them
        for org in self.Organisms:
            if org.alive:
                unit = org.id
            else:
                unit = -1
            self.grid[org.position[0]][org.position[1]] = unit

    def addOrganism(self, newOrg):
        self.Organisms += [newOrg]
        self.updateGrid()

    def printGrid(self):
        out_string = ''
        for y_array in self.grid:
            out_string += ''.join([str(x_elem) + ' ' * (6 - len(str(x_elem))) for x_elem in y_array])
            out_string += '\n'
        print(out_string)


if __name__ == '__main__':
    Ecosystem = Env(25, 100)

    Ecosystem.printGrid()
