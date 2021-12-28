from Organism import *
from graphics import *

import numpy as np
import random
import os
import ctypes

from timeit import default_timer as timer


class Resource:
    def __init__(self, grid, amt=20):
        print("Attempting to place a Resource")
        self.resources_available = amt  # This should be examined
        self.position = randomPosition(grid)
        self.empty = False

    def newYear(self):
        self.resources_available = random.randint(5, 15)

    def consume(self, Grid):
        if not self.empty:
            print(self.resources_available)
            self.resources_available -= 1
            if self.resources_available == 0:
                self.empty = True
                Grid.drawFromDict(self, empty = True)


class Grid:
    def __init__(self, grid, windowdim=[1600, 1600]):
        self.data = grid
        self.windowdim = windowdim
        self.dim = len(grid[0])
        self.position_dict = {}
        self.drawing_dict = {}
        self.y_step = windowdim[1] // self.dim
        self.x_step = windowdim[0] // self.dim
        self.beginDrawing()

    def beginDrawing(self):
        self.win = GraphWin("AI Evolution", self.windowdim[0], self.windowdim[1])

    def add_object_to_grid(self, newObject):
        # Find position and replace 0 with the organism object
        self.position_dict[newObject] = [newObject.position[0], newObject.position[1]]
        self.drawFromDict(newObject)
        # Determine what object it is
        objectTypes = []

        if str(type(newObject)) == "<class 'Organism.Organism'>":
            if newObject.alive:
                self.drawing_dict[newObject] = Circle(
                    Point((self.position_dict[newObject][1] * self.x_step) + self.x_step // 2,
                          (self.position_dict[newObject][0] * self.y_step) + self.y_step // 2),
                    self.y_step // 2)

                self.drawing_dict[newObject].setFill(color_rgb(120, 120, 120))
                self.drawing_dict[newObject].draw(self.win)
            elif newObject.corpse:
                self.drawing_dict[newObject] = Circle(
                    Point((self.position_dict[newObject][1] * self.x_step) + self.x_step // 2,
                          (self.position_dict[newObject][0] * self.y_step) + self.y_step // 2),
                    self.y_step // 2)

                self.drawing_dict[newObject].setFill(color_rgb(0, 0, 0))
                self.drawing_dict[newObject].draw(self.win)
        elif str(type(newObject)) == "<class '__main__.Resource'>":
            print(newObject)
            if not newObject.empty:
                self.drawing_dict[newObject] = Circle(
                    Point((self.position_dict[newObject][1] * self.x_step) + self.x_step // 2,
                          (self.position_dict[newObject][0] * self.y_step) + self.y_step // 2),
                    self.y_step // 2)

                self.drawing_dict[newObject].setFill(color_rgb(120, 0, 120))
                self.drawing_dict[newObject].draw(self.win)

    def drawFromDict(self, gridObject, empty=False, moving=False):
        if empty:
            self.drawing_dict[gridObject].undraw()
            self.data[self.position_dict[gridObject][0]][self.position_dict[gridObject][1]] = 0
            del self.position_dict[gridObject]
            return
        if moving:
            self.data[gridObject.last_position[0]][gridObject.last_position[1]] = 0
        self.data[self.position_dict[gridObject][0]][self.position_dict[gridObject][1]] = gridObject

    def UpdatePosition(self, gridObject, oldCoordinates, newCoordinates):
        # Put 0 in Old Coordinates
        self.position_dict[gridObject] = gridObject.position
        self.drawFromDict(gridObject, moving=True)
        dx = newCoordinates[1] - oldCoordinates[1]
        dy = newCoordinates[0] - oldCoordinates[0]
        self.drawing_dict[gridObject].move(dx*self.x_step, dy*self.y_step)

    def printGrid(self):
        print(gridToString(self.data))


class Env:
    def __init__(self, gridN, numStartingOrgs=0, nRes=None):
        self.dim = gridN
        self.grid = Grid([[0 for x in range(gridN)] for y in range(gridN)])
        self.Organisms = []
        for i in range(numStartingOrgs):
            self.addOrganism(Organism(first_gen=True, Env=self))

        self.resourceSpawns = []
        if nRes is None:
            tempAmt = gridN // 4
        else:
            tempAmt = nRes

        for i in range(tempAmt):
            self.addResourceSpawn(Resource(self.grid.data))

    def addOrganism(self, newOrg):
        self.grid.add_object_to_grid(newOrg)
        self.Organisms += [newOrg]

    def addResourceSpawn(self, resourceSpawn):
        self.resourceSpawns += [resourceSpawn]
        self.grid.add_object_to_grid(resourceSpawn)

    def tickEnv(self):
        [n.decide(self.grid) for n in self.Organisms]

    def years(self, amt=1):
        def print_resources(x):
            print(f" {x.id} : {x.current_resources} / {x.resource_demand}")
        while amt != 0:
            for i in range(100):
                self.tickEnv()
                time.sleep(0.1)

            [n.death("Starvation") for n in self.Organisms if n.current_resources < n.resource_demand ]

            [print_resources(n) for n in [x for x in self.Organisms if x.alive]]
            print(f'{len([n for n in self.Organisms if n.alive])*100/len([n for n in self.Organisms if n.murderer != "NonViable"])}%')
            amt -= 1


def main():
    Ecosystem = Env(50, 500)

    Ecosystem.grid.win.getMouse()

    Ecosystem.grid.printGrid()

    Ecosystem.years()

    Ecosystem.grid.win.getMouse()


if __name__ == '__main__':
    main()
