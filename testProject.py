#Tyson Hickey
#tjh557@mun.ca
#201507225

import sys
import random
import statistics
import math
import interfaceUtils
import mapUtils
from worldLoader import WorldSlice

# x position, z position, x size, z size
area = (0, 0, 128, 128)

#buildArea = interfaceUtils.requestBuildArea()
#if buildArea != -1:
#    x1 = buildArea["xFrom"]
#    z1 = buildArea["zFrom"]
#    x2 = buildArea["xTo"]
#    z2 = buildArea["zTo"]
#    print(buildArea)
#    area = (x1, z1, x2 - x1, z2 - z1)

#worldSlice = WorldSlice(area)
#heightmap = mapUtils.calcGoodHeightmap(worldSlice)

treeList = ["minecraft:oak_log", "minecraft:spruce_log", "minecraft:birch_log", "minecraft:jungle_log", "minecraft:acacia_log",
            "minecraft:dark_oak_log", "minecraft:brown_mushroom_block", "minecraft:red_mushroom_block",
            "minecraft:mushroom_stem", "minecraft:oak_leaves", "minecraft:spruce_leaves", "minecraft:birch_leaves",
            "minecraft:jungle_leaves", "minecraft:acacia_leaves", "minecraft:dark_oak_leaves"]

class Grid:
    def __init__(self, area):
        self.__area = [math.ceil(area[0] / 10), math.ceil(area[1] / 10), int(area[2] / 10), int(area[3] / 10)]
        self.grid = [[None for x in range(self.__area[2])] for y in range(self.__area[3])]
        self.activeCells = []

    def __str__(self):
        string = ""
        for i in range(len(self.grid)):
            string += "[ "
            for j in range(len(self.grid[0])):
                string += str(self.grid[i][j]) + " "
            string += "]\n"
        return string

    def populate(self, aliveChance, deathLimit, birthLimit, steps):

        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if random.random()*100 <= aliveChance:
                    self.grid[i][j] = True

        tempGrid = self.grid
        for step in range(steps):
            for i in range(len(self.grid)):
                for j in range(len(self.grid[0])):
                    nbs = 0
                    if i-1 >= 0 and j-1 >=0:
                        if self.grid[i-1][j-1]:
                            nbs += 1
                    if j-1 >= 0:
                        if self.grid[i][j-1]:
                            nbs += 1
                    if i+1 < len(self.grid) and j-1 >=0:
                        if self.grid[i+1][j-1]:
                            nbs += 1
                    if i-1 >= 0:
                        if self.grid[i-1][j]:
                            nbs += 1
                    if i+1 < len(self.grid):
                        if self.grid[i+1][j]:
                            nbs += 1
                    if i-1 >= 0 and j+1 < len(self.grid[0]):
                        if self.grid[i-1][j+1]:
                            nbs += 1
                    if j+1 < len(self.grid[0]):
                        if self.grid[i][j+1]:
                            nbs += 1
                    if i+1 < len(self.grid) and j+1 < len(self.grid[0]):
                        if self.grid[i+1][j+1]:
                            nbs += 1
                    if self.grid[i][j]:
                        if nbs < deathLimit:
                            tempGrid[i][j] = None
                        else:
                            tempGrid[i][j] = "Home"
                    else:
                        if nbs > birthLimit:
                            tempGrid[i][j] = "Home"
                        else:
                            tempGrid[i][j] = None
            self.grid = tempGrid
        self.activeCells = []
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j]:
                    self.activeCells.append([[i, j], None])

    def closestCell(self, x, z):
        tempList = []
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j]:
                    tempList.append([[i, j], abs(x-i) + abs(z-j)])
        sortedList = sorted(tempList, key = lambda x: x[1])
        sortedList.pop(0)
        for i in range(len(sortedList)):
            for j in range(len(self.activeCells)):
                if x is self.activeCells[j][0][0] and z is self.activeCells[j][0][1] and self.activeCells[j][1] is None:
                    self.activeCells[j][1] = [sortedList[i][0][0], sortedList[i][0][1]]
                    return
                    #return [sortedList[i][0][0], sortedList[i][0][1]]

    def spanningTree(self):
        for i in range(len(self.activeCells)):
            self.closestCell(self.activeCells[i][0][0], self.activeCells[i][0][1])

    def createPaths(self):
        for i in range(len(self.activeCells)):
            for x in range(self.activeCells[i][0][0]+1, self.activeCells[i][1][0]):
                self.grid[x][self.activeCells[i][0][1]] = "Path"
            for z in range(self.activeCells[i][0][1]+1, self.activeCells[i][1][1]):
                self.grid[self.activeCells[i][1][0]][z] = "Path"


    def generateVillage(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j]:
                    self.grid[i][j].build(i, j)

class structure:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        string = "[Name: " + self.name + "]"
        return string

    def build(self, x, z):
        TODO

grid = Grid(area)
print(grid)
grid.populate(50, 3, 5, 10)
print(grid)
print(grid.activeCells)
grid.spanningTree()
print(grid.activeCells)
grid.createPaths()
print(grid)
