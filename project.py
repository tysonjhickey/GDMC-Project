#Tyson Hickey
#tjh557@mun.ca
#201507225

import sys
import random
import copy
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

def heightAt(x, z):
    return heightmap[(x - area[0], z - area[1])]

def setBlock(x, y, z, block):
    interfaceUtils.setBlock(x, y, z, block)

def getBlock(x, y, z):
    return interfaceUtils.getBlock(x, y, z)

class Grid:
    def __init__(self, area, division):
        #self.__area = [math.ceil(area[0] / 15), math.ceil(area[1] / 15), int(area[2] / 15), int(area[3] / 15)]           
        #self.__area = copy.deepcopy(area)
        self.XZ = [area[0], area[1]]
        self.dimensions = [int(area[2]/division), int(area[3]/division)]
        self.grid = [Cell()]*(int(area[2]/division)*int(area[2]/division))

    def __str__(self):
        string = "Grid:\n"
        for z in range(self.dimensions[1]):
            string += "[ "
            for x in range(self.dimensions[0]):
                string += str(self.grid[self.dimensions[0] * z + x].getIdentifier()) + " "
            string += "]\n"
        return string

    # width * z + x
    def setCell(self, x, z, cell):
        self.grid[self.width * z + x] = cell

class Cell:
    def __init__(self, identifier=0, edges=[]):
        self.__identifier = identifier
        self.__edges = edges

    def __str__(self):
        string = "Identifier: " + str(self.__identifier)

    def getIdentifier(self):
        return self.__identifier

grid = Grid(area, 15)
print(grid)
