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

def isClosed(nextNode, node):
    #print("isClosed" + str(node[2]))
    for i in range(len(node[2])):
        if node[2][i][0] == nextNode[0] and node[2][i][1] == nextNode[1]:
            return True
    return False

class Grid:
    def __init__(self, area):
        self.__area = [math.ceil(area[0] / 15), math.ceil(area[1] / 15), int(area[2] / 15), int(area[3] / 15)]
        self.grid = [[None for x in range(self.__area[2])] for y in range(self.__area[3])]

    def __str__(self):
        string = "Structure Grid: \n"
        for i in range(len(self.grid)):
            string += "[ "
            for j in range(len(self.grid[0])):
                if self.grid[i][j] == None:
                    string += str(0) + " "
                elif (self.grid[i][j] and self.grid[i][j].isImpass()):
                    string += str(2) + " "
                else:
                    string += str(1) + " "
            string += "]\n"
        return string

    def populate(self, aliveChance, deathLimit, birthLimit, steps):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if random.randint(1, 100) <= aliveChance:
                    self.grid[i][j] = Structure([i, j])

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
                            tempGrid[i][j] = Structure([i, j])
                    else:
                        if nbs > birthLimit:
                            tempGrid[i][j] = Structure([i, j])
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
                            self.grid[i][j] = Structure([i, j])

    def checkMountains(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if random.randint(1, 100) <= 25:
                    if not self.grid[i][j]:
                        self.grid[i][j] = Structure([i, j], "Mountain", True)

        #for i in range(len(self.grid)):
        #    for j in range(len(self.grid[0])):
        #        if self.grid[i][j]:
        #            x = i*15
        #            z = j*15
        #            for k in range(x, x+14):
        #                for l in range(z, z+14):
        #                    if (abs(heightAt(k, l) - heightAt(k+1, z)) > 2 or abs(heightAt(k, l) - heightAt(k, z+1)) > 2):
        #                        self.grid[i][j] = Structure("Mountain", True)


    #def distanceBFS(self, x, z, structure):
    #    open = []
    #    if x+1 < len(self.grid) and (self.grid[x+1][z] == None or self.grid[x+1][z] and not self.grid[x+1][z].isImpass()):
    #        open.append([[x+1, z], 1, [[x,z]]])
    #    if x-1 >= 0 and (self.grid[x-1][z] == None or self.grid[x-1][z] and not self.grid[x-1][z].isImpass()):
    #        open.append([[x-1, z], 1, [[x,z]]])
    #    if z+1 < len(self.grid[0]) and (self.grid[x][z+1] == None or self.grid[x][z+1] and not self.grid[x][z+1].isImpass()):
    #        open.append([[x, z+1], 1, [[x,z]]])
    #    if z-1 >= 0 and (self.grid[x][z-1] == None or self.grid[x][z-1] and not self.grid[x][z-1].isImpass()):
    #        open.append([[x, z-1], 1, [[x,z]]])
    #    #closed = [[False for x in range(self.__area[2])] for y in range(self.__area[3])]
    #    while(len(open) > 0):
    #        node = open.pop(0)
    #        if self.grid[node[0][0]][node[0][1]]:
    #            structure.addEdge([[node[0][0], node[0][1]], node[1], node[2]])
    #        else:
    #            if node[0][0]+1 < len(self.grid) and (self.grid[node[0][0]+1][node[0][1]] == None or self.grid[node[0][0]+1][node[0][1]] and not self.grid[node[0][0]+1][node[0][1]].isImpass()) and not inClosed(node[0][0]+1, node[0][1], node):
    #                print(open)
    #                print("\n")
    #                open.append([[node[0][0]+1, node[0][1]], node[1]+1, node[2].append([node[0][0], node[0][1]])])
    #            if node[0][0]-1 >= 0 and (self.grid[node[0][0]-1][node[0][1]] == None or self.grid[node[0][0]-1][node[0][1]] and not self.grid[node[0][0]-1][node[0][1]].isImpass()) and not inClosed(node[0][0]-1, node[0][1], node):
    #                open.append([[node[0][0]-1, node[0][1]], node[1]+1, node[2].append([node[0][0], node[0][1]])])
    #            if node[0][1]+1 < len(self.grid[0]) and (self.grid[node[0][0]][node[0][1]+1] == None or self.grid[node[0][0]][node[0][1]+1] and not self.grid[node[0][0]][node[0][1]+1].isImpass()) and not inClosed(node[0][0], node[0][1]+1, node):
    #                open.append([[node[0][0], node[0][1]+1], node[1]+1, node[2].append([node[0][0], node[0][1]])])
    #            if node[0][1]-1 >= 0 and (self.grid[node[0][0]][node[0][1]-1] == None or self.grid[node[0][0]][node[0][1]-1] and not self.grid[node[0][0]][node[0][1]-1].isImpass()) and not inClosed(node[0][0], node[0][1]-1, node):
    #                open.append([[node[0][0], node[0][1]-1], node[1]+1, node[2].append([node[0][0], node[0][1]])])
    # Edge = [[x,z], dist, [[x,z], ...]]
    def distanceBFS(self, structure):
        open = []
        x = structure.getCoordinate()[0]
        z = structure.getCoordinate()[1]
        if self.grid[x][z] and self.grid[x][z].isImpass():
            return
        if (x+1 < len(self.grid) and (not self.grid[x+1][z] or self.grid[x+1][z] and not self.grid[x+1][z].isImpass())):
            open.append([[x+1,z], 1, [[x,z]]])
        if (z+1 < len(self.grid[0]) and (not self.grid[x][z+1] or self.grid[x][z+1] and not self.grid[x][z+1].isImpass())):
            open.append([[x,z+1], 1, [[x,z]]])
        if (x-1 >= 0 and (not self.grid[x-1][z] or self.grid[x-1][z] and not self.grid[x-1][z].isImpass())):
            open.append([[x-1,z], 1, [[x,z]]])
        if (z-1 > 0 and (not self.grid[x][z-1] or self.grid[x][z-1] and not self.grid[x][z-1].isImpass())):
            open.append([[x,z-1], 1, [[x,z]]])
        while(len(open) > 0):
            node = open.pop(0)
            if self.grid[node[0][0]][node[0][1]]:
                structure.addEdge(node)
            else:
                if node[0][0]+1 < len(self.grid) and (not self.grid[node[0][0]+1][node[0][1]] or self.grid[node[0][0]+1][node[0][1]] and not self.grid[node[0][0]+1][node[0][1]].isImpass()) and not isClosed([node[0][0]+1, node[0][1]], node):
                    #print("Number1: "+ str(node[2]))
                    tempNode = copy.deepcopy(node)
                    tempNode[2].append([node[0][0], node[0][1]])
                    open.append([[tempNode[0][0]+1, tempNode[0][1]], tempNode[1]+1, tempNode[2]])
                if node[0][1]+1 < len(self.grid[0]) and (not self.grid[node[0][0]][node[0][1]+1] or self.grid[node[0][0]][node[0][1]+1] and not self.grid[node[0][0]][node[0][1]+1].isImpass()) and not isClosed([node[0][0], node[0][1]+1], node):
                    #print("Number2: "+ str(node[2]))
                    tempNode = copy.deepcopy(node)
                    tempNode[2].append([node[0][0], node[0][1]])
                    open.append([[tempNode[0][0], tempNode[0][1]+1], tempNode[1]+1, tempNode[2]])
                if node[0][0]-1 >= 0 and (not self.grid[node[0][0]-1][node[0][1]] or self.grid[node[0][0]-1][node[0][1]] and not self.grid[node[0][0]-1][node[0][1]].isImpass()) and not isClosed([node[0][0]-1, node[0][1]], node):
                    #print("Number3: "+ str(node[2]))
                    tempNode = copy.deepcopy(node)
                    tempNode[2].append([node[0][0], node[0][1]])
                    open.append([[tempNode[0][0]-1, tempNode[0][1]], tempNode[1]+1, tempNode[2]])
                if node[0][1]-1 >= 0 and (not self.grid[node[0][0]][node[0][1]-1] or self.grid[node[0][0]][node[0][1]-1] and not self.grid[node[0][0]][node[0][1]-1].isImpass()) and not isClosed([node[0][0], node[0][1]-1], node):
                    #print("Number4: "+ str(node[2]))
                    tempNode = copy.deepcopy(node)
                    tempNode[2].append([node[0][0], node[0][1]])
                    open.append([[tempNode[0][0], tempNode[0][1]-1], tempNode[1]+1, tempNode[2]])

    def DFSCycleCheck(self, structureList):

    def MST(self):
        structureList = []
        edgeList = []
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j] and not self.grid[i][j].isImpass():
                    self.grid[i][j].bestPath = self.grid[i][j].edges[][2][0]
                    structureList.append(self.grid[i][j])
        
        while not self.DFSCycleCheck(structureList):
            return

class Structure:
    def __init__(self, coordinate=[], name="Structure", impass=False):
        self.coordinate = coordinate
        self.name = name
        self.impass = impass
        self.edges = []
        self.bestPath = None

    def __str__(self):
        string = "{ Coordinate: " + str(self.coordinate) + ", Name: " + str(self.name) + ", Impass: " + str(self.impass) + "}\nEdges:\n" + "{\n"
        for i in range(len(self.edges)):
            string += "    " + str(self.edges[i]) + "\n"
        string += "}\n"
        return string

    def getCoordinate(self):
        return self.coordinate

    def setCoordinate(self, coordinate):
        self.coordinate = coordinate

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def isImpass(self):
        return self.impass

    def setImpass(self):
        self.impass = True

    def notImpass(self):
        self.impass = False

    def addEdge(self, edge):
        self.edges.append(edge)

    def setPath(self, pathList):
        self.path = pathList

    def build(self):
        return


def bfsCheck(grid):
    for i in range(len(grid.grid)):
        for j in range(len(grid.grid[0])):
            if grid.grid[i][j] and not grid.grid[i][j].isImpass():
                grid.distanceBFS(grid.grid[i][j])
                print(grid.grid[i][j].edges[0])

grid = Grid(area)
grid.populate(25, 3, 5, 10)
grid.populateSparseArea()
grid.checkMountains()
print(grid)
bfsCheck(grid)


