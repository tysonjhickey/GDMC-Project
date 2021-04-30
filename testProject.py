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

def heightAt(x, z):
    return heightmap[(x - area[0], z - area[1])]

def setBlock(x, y, z, block):
    interfaceUtils.setBlock(x, y, z, block)

def getBlock(x, y, z):
    return interfaceUtils.getBlock(x, y, z)

class Grid:
    def __init__(self, area):
        self.__area = [math.ceil(area[0] / 10), math.ceil(area[1] / 10), int(area[2] / 10), int(area[3] / 10)]
        self.grid = [[None for x in range(self.__area[2])] for y in range(self.__area[3])]
        self.activeCells = [[None for x in range(self.__area[2])] for y in range(self.__area[3])]

    def __str__(self):
        string = "Structure Grid: \n"
        for i in range(len(self.grid)):
            string += "[ "
            for j in range(len(self.grid[0])):
                string += str(self.grid[i][j]) + " "
            string += "]\n"

        string += "Closest Structure Grid: \n"
        for i in range(len(self.activeCells)):
            string += "[ "
            for j in range(len(self.activeCells[0])):
                string += str(self.activeCells[i][j]) + " "
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
                            tempGrid[i][j] = structure("Structure")
                    else:
                        if nbs > birthLimit:
                            tempGrid[i][j] = structure("Structure")
                        else:
                            tempGrid[i][j] = None
            self.grid = tempGrid

    def populateSparseArea(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if not self.grid[i][j]:
                    temp = random.randint(1, 100)
                    if temp <= 25:
                        if (
                            i-1 >= 0 and not self.grid[i-1][j] and
                            i+1 < len(self.grid) and not self.grid[i+1][j] and 
                            j-1 >= 0 and not self.grid[i][j-1] and
                            j+1 < len(self.grid[0]) and not self.grid[i][j+1]
                        ):
                            self.grid[i][j] = structure("Structure")

    def closestCell(self, x, z):
        tempList = []
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j]:
                    tempList.append([[i, j], abs(x-i) + abs(z-j)])
        sortedList = sorted(tempList, key = lambda x: x[1])
        #self.activeCells[x][z] = True
        sortedList.pop(0)
        for i in range(len(sortedList)):
            if not self.activeCells[sortedList[i][0][0]][sortedList[i][0][1]]:
                self.activeCells[x][z] = [sortedList[i][0][0], sortedList[i][0][1]]
                return
            

    def spanningTree(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j]:
                    self.closestCell(i, j) 

    def createPaths(self):
        for i in range(len(self.activeCells)):
            for j in range(len(self.activeCells[0])):
                if self.activeCells[i][j]:
                    if i < self.activeCells[i][j][0]:
                        for x in range(i, self.activeCells[i][j][0]):
                            if self.grid[x][j] == None:
                                self.grid[x][j] = structure("Path")
                    elif i > self.activeCells[i][j][0]:
                        for x in range(self.activeCells[i][j][0], i):
                            if self.grid[x][j] == None:
                                self.grid[x][j] = structure("Path")
                    if j < self.activeCells[i][j][1]:
                        for y in range(j, self.activeCells[i][j][1]):
                            if self.grid[self.activeCells[i][j][0]][y] == None:
                                self.grid[self.activeCells[i][j][0]][y] = structure("Path")
                    elif j > self.activeCells[i][j][1]:
                        for y in range(self.activeCells[i][j][1], j):
                            if self.grid[self.activeCells[i][j][0]][y] == None:
                                self.grid[self.activeCells[i][j][0]][y] = structure("Path")
        
        #for i in range(len(self.grid)):
        #    for j in range(len(self.grid[0])):
        #        if self.grid[i][j] and self.grid[i][j].getName() == "Structure":
        #            if (i-1 >= 0 and j-1 >= 0 and self.grid[i-1][j-1]):
        #                if not self.grid[i-1][j]:
        #                    self.grid[i-1][j] = structure("Path")
        #                elif not self.grid[i][j-1]:
        #                    self.grid[i][j-1] = structure("Path")
        #            elif (i+1 < len(self.grid) and j-1 >= 0 and self.grid[i+1][j-1]):
        #                if not self.grid[i][j-1]:
        #                    self.grid[i][j-1] = structure("Path")
        #                elif not self.grid[i+1][j]:
        #                    self.grid[i+1][j] = structure("Path")
        #            elif (i-1 >= 0 and j+1 < len(self.grid[0]) and self.grid[i-1][j+1]):
        #                if not self.grid[i-1][j]:
        #                    self.grid[i-1][j] = structure("Path")
        #                elif not self.grid[i][j+1]:
        #                    self.grid[i][j+1] = structure("Path")
        #            elif (i+1 < len(self.grid) and j+1 < len(self.grid[0]) and self.grid[i+1][j+1]):
        #                if not self.grid[i+1][j]:
        #                    self.grid[i+1][j] = structure("Path")
        #                elif not self.grid[i][j+1]:
        #                    self.grid[i][j+1] = structure("Path")


    def randomize(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if (self.grid[i][j] and self.grid[i][j].getName() == "Structure"):
                    temp = random.randint(1, 100)
                    if temp <= 5:
                        self.grid[i][j].setName("Castle")
                    elif temp <= 30:
                        self.grid[i][j].setName("Home")
                    elif temp <= 55:
                        self.grid[i][j].setName("Home2")
                    elif temp <= 80:
                        self.grid[i][j].setName("Home3")
                    else:
                        self.grid[i][j].setName("Fountain")

    def checkMountains(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j]:
                    x = i*10
                    z = j*10
                    for k in range(x, x+9):
                        for l in range(z, z+9):
                            if (abs(heightAt(k, l) - heightAt(k+1, z)) > 2 or abs(heightAt(k, l) - heightAt(k, z+1)) > 2):
                                self.grid[i][j] = structure("Mountain")


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

    def setName(self, newName):
        self.name = newName

    def getName(self):
        return self.name

    def build(self, x, z):
        x = x*10
        z = z*10
        if self.name == "Path":
            return
        elif self.name == "Home":
            for i in range(x, x+10):
                setBlock(i, heightAt(i, z), z, "oak_fence")
                setBlock(i, heightAt(i, z+9), z+9, "oak_fence")
            for i in range(z, z+10):
                setBlock(x, heightAt(x, i), i, "oak_fence")
                setBlock(x+9, heightAt(x+9, i), i, "oak_fence")
            for i in range(x+2, x+8):
                for j in range(z+2, z+8):
                    setBlock(i, heightAt(i, j)-1, j, "oak_planks")
            for j in range(0, 3):
                for i in range(x+2, x+8):
                    setBlock(i, heightAt(i, z+2)+j, z+2, "oak_planks")
                    setBlock(i, heightAt(i, z+7)+j, z+7, "oak_planks")
                for k in range(z+2, z+8):
                    setBlock(x+2, heightAt(x+2, k)+j, k, "oak_planks")
                    setBlock(x+7, heightAt(x+7, k)+j, k, "oak_planks")
            for i in range(x+2, x+8):
                for j in range(z+2, z+8):
                    setBlock(i, heightAt(i, j)+3, j, "oak_planks")
        elif self.name == "Fountain":
            return
        elif self.name == "Home2":
            return
        elif self.name == "Home3":
            return
        #elif self.name == "Structure":
        #    for i in range(x, x+10):
        #        for j in range(z, z+10):
        #            setBlock(i, heightAt(i, j), j, "oak_planks")
        #    for i in range(x, x+10):
        #        setBlock(i, heightAt(i, z)+1, z, "oak_fence")
        #        setBlock(i, heightAt(i, z+9)+1, z+9, "oak_fence")
        #    for i in range(z, z+10):
        #        setBlock(x, heightAt(x, i)+1, i, "oak_fence")
        #        setBlock(x+9, heightAt(x+9, i)+1, i, "oak_fence")

#Builds fence aroud given build area
for x in range(area[0], area[0] + area[2]):
    z = area[1]
    y = heightAt(x, z)
    setBlock(x, y - 1, z, "cobblestone")
    setBlock(x, y,   z, "oak_fence")
for z in range(area[1], area[1] + area[3]):
    x = area[0]
    y = heightAt(x, z)
    setBlock(x, y - 1, z, "cobblestone")
    setBlock(x, y, z, "oak_fence")
for x in range(area[0], area[0] + area[2]):
    z = area[1] + area[3] - 1
    y = heightAt(x, z)
    setBlock(x, y - 1, z, "cobblestone")
    setBlock(x, y,   z, "oak_fence")
for z in range(area[1], area[1] + area[3]):
    x = area[0] + area[2] - 1
    y = heightAt(x, z)
    setBlock(x, y - 1, z, "cobblestone")
    setBlock(x, y, z, "oak_fence")


grid = Grid(area)
grid.populate(10, 3, 3, 10)
grid.populateSparseArea()
grid.randomize()
grid.checkMountains()
grid.spanningTree()
grid.createPaths()
grid.generateVillage()
print(grid)
