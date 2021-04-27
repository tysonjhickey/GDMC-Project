#Tyson Hickey
#tjh557@mun.ca
#201507225

import random
import statistics
import math
import interfaceUtils
import mapUtils
from worldLoader import WorldSlice

# x position, z position, x size, z size
area = (0, 0, 128, 128)

buildArea = interfaceUtils.requestBuildArea()
if buildArea != -1:
    x1 = buildArea["xFrom"]
    z1 = buildArea["zFrom"]
    x2 = buildArea["xTo"]
    z2 = buildArea["zTo"]
    print(buildArea)
    area = (x1, z1, x2 - x1, z2 - z1)

worldSlice = WorldSlice(area)
heightmap = mapUtils.calcGoodHeightmap(worldSlice)

treeList = ["minecraft:oak_log", "minecraft:spruce_log", "minecraft:birch_log", "minecraft:jungle_log", "minecraft:acacia_log",
            "minecraft:dark_oak_log", "minecraft:brown_mushroom_block", "minecraft:red_mushroom_block",
            "minecraft:mushroom_stem", "minecraft:oak_leaves", "minecraft:spruce_leaves", "minecraft:birch_leaves",
            "minecraft:jungle_leaves", "minecraft:acacia_leaves", "minecraft:dark_oak_leaves"]

class Grid:
    def __init__(self, area):
        self.__area = [math.ceil(area[0] / 10), math.ceil(area[1] / 10), int(area[2] / 10), int(area[3] / 10)]
        self.grid = [[None for x in range(self.__area[2])] for y in range(self.__area[3])]

    def __str__(self):
        string = ""
        for i in range(0, len(self.grid)):
            string += "[ "
            for j in range(0, len(self.grid[0])):
                string += str(self.grid[i][j]) + " "
            string += "]\n"
        return string

    def placementGeneration(self, aliveChance, deathLimit, birthLimit, steps):

        for i in range(0, len(self.grid)):
            for j in range(0, len(self.grid[0])):
                if random.random()*100 <= aliveChance:
                    self.grid[i][j] = True

        tempGrid = self.grid
        for step in range(0, steps):
            for i in range(0, len(self.grid)):
                for j in range(0, len(self.grid[0])):
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

    def generateVillage(self):
        for i in range(0, len(self.grid)):
            for j in range(0, len(self.grid[0])):
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