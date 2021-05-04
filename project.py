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

def isIn(node, nodeList):
    for i in range(len(nodeList)):
        if node[0] == nodeList[i][0] and node[1] == nodeList[i][1]:
            return True
    return False

def trim(edgeList):
    trimmedList = []
    for i in range(len(edgeList)):
        if len(edgeList[i]) > 2:
            trimmedList.append(edgeList[i])
    for i in range(len(trimmedList)):
        for j in range(len(trimmedList)):
            if i != j and trimmedList[i] != None and trimmedList[j] != None:
                if (trimmedList[i][0] == trimmedList[j][0] and trimmedList[i][-1] == trimmedList[j][-1]) or (trimmedList[i][0] == trimmedList[j][-1] and trimmedList[i][-1] == trimmedList[j][0]):
                    if len(trimmedList[i]) > len(trimmedList[j]):
                        trimmedList[i] = None
                    else:
                        trimmedList[j] = None
    trimmedList = [i for i in trimmedList if i]
    return trimmedList


class Grid:
    def __init__(self, area, division):
        self.area = area
        self.division = division
        self.grid = [[Cell() for x in range(int(area[2]/division))] for y in range(int(area[3]/division))]

    def __str__(self):
        string = "Grid: \n"
        for z in range(len(self.grid[0])):
            string += "[ "
            for x in range(len(self.grid)):
                string += str(self.grid[x][z].identifier) + " "
            string += "]\n"
        return string

    def printCells(self):
        for z in range(len(self.grid[0])):
            for x in range(len(self.grid)):
                if self.grid[x][z].identifier == 3:
                    print("[" + str(x) + ", " + str(z) + "]\n")
                    print(self.grid[x][z])

    def getNeighbours(self, x, z):
        nbs = 0
        if z-1 >= 0 and self.grid[x][z-1].identifier == 3:
            nbs += 1
        if x-1 >= 0 and self.grid[x-1][z].identifier == 3:
            nbs += 1
        if z+1 < len(self.grid[0]) and self.grid[x][z+1].identifier == 3:
            nbs += 1
        if x+1 < len(self.grid) and self.grid[x+1][z].identifier == 3:
            nbs += 1
        return nbs  

    def returnNeighbours(self, x, z):
        nbs = [False, False, False, False]
        if z-1 >= 0 and self.grid[x][z-1].identifier != 2 and self.grid[x][z-1].identifier != 0:
            nbs[0] = True
        if x-1 >= 0 and self.grid[x-1][z].identifier != 2 and self.grid[x-1][z].identifier != 0:
            nbs[1] = True
        if z+1 < len(self.grid[0]) and self.grid[x][z+1].identifier != 2 and self.grid[x][z+1].identifier != 0:
            nbs[2] = True
        if x+1 < len(self.grid) and self.grid[x+1][z].identifier != 2 and self.grid[x+1][z].identifier != 0:
            nbs[3] = True
        return nbs

    def populate(self, aliveChance, deathLimit=0, birthLimit=0, steps=0):
        for z in range(len(self.grid[0])):
            for x in range(len(self.grid)):
                if random.randint(1, 100) <= aliveChance:
                    self.grid[x][z].identifier = 3

        if steps == 0:
            return
        elif steps > 0:
            tempGrid = copy.deepcopy(self.grid)
            for step in range(steps):
                for z in range(len(self.grid[0])):
                    for x in range(len(self.grid)):
                        nbs = self.getNeighbours(x, z)
                        if self.grid[x][z].identifier == 3:
                            if nbs < deathLimit:
                                tempGrid[x][z].identifier = 0
                            else:
                                tempGrid[x][z].identifier = 3
                        else:
                            if nbs > birthLimit:
                                tempGrid[x][z].identifier = 3
                            else:
                                tempGrid[x][z].identifier = 0
        else:
            print ("Error; Using default setting")
            return

    def checkMountains(self):
        for z in range(len(self.grid[0])):
            for x in range(len(self.grid)):
                if random.randint(1, 100) <= 25:
                    if self.grid[x][z].identifier != 3:
                        self.grid[x][z].identifier = 2

    def getOtherCells(self, _x, _z):
        cells = []
        for z in range(len(self.grid[0])):
            for x in range(len(self.grid)):
                if self.grid[x][z].identifier == 3 and (x != _x or z != _z):
                    cells.append([x, z])
        return cells

    def getEdges(self, limit=-1):
        for z in range(len(self.grid[0])):
            for x in range(len(self.grid)):
                if self.grid[x][z].identifier == 3:
                    goalList = self.getOtherCells(x, z)
                    openList = [[[x, z]]]
                    while(len(openList) > 0):
                        node = openList.pop(0)
                        #print(node)
                        nodeX = node[-1][0]
                        nodeZ = node[-1][1]
                        #print(node[-1])
                        if isIn(node[-1], goalList):
                            tempNode = copy.deepcopy(node)
                            self.grid[x][z].edges.append(tempNode)
                            if limit != -1 and len(self.grid[x][z].edges) > limit:
                                break
                        if nodeZ-1 >= 0 and self.grid[nodeX][nodeZ-1].identifier != 2 and not isIn([nodeX, nodeZ-1], node):
                            tempNode = copy.deepcopy(node)
                            tempNode.append([nodeX, nodeZ-1])
                            openList.append(tempNode)
                        if nodeX-1 >= 0 and self.grid[nodeX-1][nodeZ].identifier != 2 and not isIn([nodeX-1, nodeZ], node):
                            tempNode = copy.deepcopy(node)
                            tempNode.append([nodeX-1, nodeZ])
                            openList.append(tempNode)
                        if nodeZ+1 < len(self.grid[0]) and self.grid[nodeX][nodeZ+1].identifier != 2 and not isIn([nodeX, nodeZ+1], node):
                            tempNode = copy.deepcopy(node)
                            tempNode.append([nodeX, nodeZ+1])
                            openList.append(tempNode)
                        if nodeX+1 < len(self.grid) and self.grid[nodeX+1][nodeZ].identifier != 2 and not isIn([nodeX+1, nodeZ], node):
                            tempNode = copy.deepcopy(node)
                            tempNode.append([nodeX+1, nodeZ])
                            openList.append(tempNode)

    def allVisited(self):
        notVisited = 0
        for z in range(len(self.grid[0])):
            for x in range(len(self.grid)):
                if self.grid[x][z].identifier == 3:
                    if not self.grid[x][z].visited:
                        notVisited += 1
        if notVisited > 0:
            return False
        return True

    def setNeighboursVisited(self, x, z):
        if z-1 >= 0 and self.grid[x][z-1].identifier == 3 and not self.grid[x][z-1].visited:
            self.grid[x][z-1].visited = True
            self.setNeighboursVisited(x, z-1)
        if x-1 >= 0 and self.grid[x-1][z].identifier == 3 and not self.grid[x-1][z].visited:
            self.grid[x-1][z].visited = True
            self.setNeighboursVisited(x-1, z)
        if z+1 < len(self.grid[0]) and self.grid[x][z+1].identifier == 3 and not self.grid[x][z+1].visited:
            self.grid[x][z+1].visited = True
            self.setNeighboursVisited(x, z+1)
        if x+1 < len(self.grid) and self.grid[x+1][z].identifier == 3 and not self.grid[x+1][z].visited:
            self.grid[x+1][z].visited = True
            self.setNeighboursVisited(x+1, z)
            
    def setVisited(self, edge):
        x = edge[0][0]
        x2 = edge[-1][0]
        z = edge[0][1]
        z2 = edge[-1][1]
        self.grid[x][z].visited = True
        self.grid[x2][z2].visited = True
        self.setNeighboursVisited(x, z)
        self.setNeighboursVisited(x2, z2)
    
    def mst(self):
        edgeBank = []
        nodes = 0
        for z in range(len(self.grid[0])):
            for x in range(len(self.grid)):
                if self.grid[x][z].identifier == 3:
                    nodes += 1
                    for i in range(len(self.grid[x][z].edges)):
                        edgeBank.append(self.grid[x][z].edges[i])
        for i in range(len(edgeBank)):
            if len(edgeBank[i]) <= 2:
                edgeBank[i] = None
        edgeBank = [i for i in edgeBank if i]
        edgeBank = sorted(edgeBank, key=len)
        mst = []
        while(not self.allVisited() and len(edgeBank) > 0):
            edge = edgeBank.pop(0)
            if (not self.grid[edge[0][0]][edge[0][1]].visited or not self.grid[edge[-1][0]][edge[-1][1]].visited):
                mst.append(edge)
                self.setVisited(edge)
        return mst
        
    def pathify(self, edges):
        for i in range(len(edges)):
            for j in range(1, len(edges[i])-1):
                self.grid[edges[i][j][0]][edges[i][j][1]].identifier = 1

    def level(self, x, z):
        h = []
        for i in range(x, x+16):
            for j in range(z, z+16):
                h.append(heightAt(i, j)-1)
        h.sort()
        h = statistics.mode(h)
        for i in range(x, x+16):
            for j in range(z, z+16):
                if heightAt(i, j)-1 > h:
                    height = heightAt(i, j)-1
                    while(height != h):
                        setBlock(i, height, j, "air")
                        height -= 1
                elif heightAt(i, j)-1 < h:
                    height = heightAt(i, j)-1
                    block = getBlock(i, height-1, j)
                    while(height != h):
                        setBlock(i, height, j, block)
                        height += 1
 #       for j in range(h, h+10):
 #           for i in range(x, x+16):
 #               for k in range(z, z+16):
 #                   if getBlock(i, j, k) in treeList:
 #                       setBlock(i, j, k, "air")
        return h

    def build(self):
        for z in range(len(self.grid[0])):
            for x in range(len(self.grid)):
                if self.grid[x][z].identifier != 0: # and self.grid[x][z].identifier != 2:
                    #NORTH>WEST>SOUTH>EAST
                    connectingCells = self.returnNeighbours(x, z)
                    startX = self.area[0] + x*self.division
                    startZ = self.area[1] + z*self.division
                    endX = self.area[0] + x*self.division + self.division
                    endZ = self.area[1] + z*self.division + self.division
                    h = self.level(startX, startZ)

                    #Builds the paths
                    if self.grid[x][z].identifier == 1:
                        for i in range(startX+6, startX+10):
                            for j in range(startZ+6, startZ+10):
                                setBlock(i, h, j, "stone_bricks")
                        setBlock(startX+6, h+1, startZ+6, "stone_brick_slab")
                        setBlock(startX+9, h+1, startZ+9, "stone_brick_slab")
                        setBlock(startX+9, h+1, startZ+6, "stone_brick_slab")
                        setBlock(startX+6, h+1, startZ+9, "stone_brick_slab")
                        if connectingCells[0]:
                            for i in range(startX+6, startX+10):
                                for j in range(startZ, startZ+6):
                                    setBlock(i, h, j, "stone_bricks")
                            for j in range(startZ, startZ+6):
                                setBlock(startX+6, h+1, j, "stone_brick_slab")
                                setBlock(startX+9, h+1, j, "stone_brick_slab")
                        else:
                            setBlock(startX+7, h+1, startZ+6, "stone_brick_slab")
                            setBlock(startX+8, h+1, startZ+6, "stone_brick_slab")
                        if connectingCells[1]:
                            for i in range(startX, startX+6):
                                for j in range(startZ+6, startZ+10):
                                    setBlock(i, h, j, "stone_bricks")
                            for i in range(startX, startX+6):
                                setBlock(i, h+1, startZ+6, "stone_brick_slab")
                                setBlock(i, h+1, startZ+9, "stone_brick_slab")
                        else:
                            setBlock(startX+6, h+1, startZ+7, "stone_brick_slab")
                            setBlock(startX+6, h+1, startZ+8, "stone_brick_slab")
                        if connectingCells[2]:
                            for i in range(startX+6, startX+10):  
                                for j in range(startZ+10, startZ+16):
                                    setBlock(i, h, j, "stone_bricks")
                            for j in range(startZ+10, startZ+16):
                                setBlock(startX+6, h+1, j, "stone_brick_slab")
                                setBlock(startX+9, h+1, j, "stone_brick_slab")
                        else:
                            setBlock(startX+7, h+1, startZ+9, "stone_brick_slab")
                            setBlock(startX+8, h+1, startZ+9, "stone_brick_slab")
                        if connectingCells[3]:
                            for i in range(startX+10, startX+16):
                                for j in range(startZ+6, startZ+10):
                                    setBlock(i, h, j, "stone_bricks")
                            for i in range(startX+10, startX+16):
                                setBlock(i, h+1, startZ+6, "stone_brick_slab")
                                setBlock(i, h+1, startZ+9, "stone_brick_slab")
                        else:
                            setBlock(startX+9, h+1, startZ+7, "stone_brick_slab")
                            setBlock(startX+9, h+1, startZ+8, "stone_brick_slab")
                                
                    elif self.grid[x][z].identifier == 2:
                        for i in range(startX, endX):
                            for j in range(startZ, endZ):
                                setBlock(i, heightAt(i, j), j, "bedrock")

                    #Cabin
                    elif self.grid[x][z].identifier == 3:
                        for i in range(startX, startX+16):
                            setBlock(i, h+1, startZ, "oak_fence")
                            setBlock(i, h+1, startZ+15, "oak_fence")
                        for j in range(startZ, startZ+16):
                            setBlock(startX, h+1, j, "oak_fence")
                            setBlock(startX+15, h+1, j, "oak_fence")

                        for i in range(startX+4, startX+12):
                            for j in range(startZ+4, startZ+12):
                                setBlock(i, h, j, "spruce_planks")
                                setBlock(i, h+4, j, "spruce_planks")

                        for j in range(h+1, h+4):
                            for i in range(startX+4, startX+12):
                                setBlock(i, j, startZ+4, "dark_oak_planks")
                                setBlock(i, j, startZ+11, "dark_oak_planks")
                            for k in range(startZ+4, startZ+12):
                                setBlock(startX+4, j, k, "dark_oak_planks")
                                setBlock(startX+11, j, k, "dark_oak_planks")

                        for i in range(startX+4, startX+12):
                            setBlock(i, h+4, startZ+4, "oak_log")
                            setBlock(i, h+4, startZ+11, "oak_log")

                        for k in range(startZ+4, startZ+12):
                            setBlock(startX+4, h+4, k, "oak_log")
                            setBlock(startX+11, h+4, k, "oak_log")

                        for j in range(h, h+4):
                            setBlock(startX+4, j, startZ+4, "oak_log")
                            setBlock(startX+11, j, startZ+4, "oak_log")
                            setBlock(startX+4, j, startZ+11, "oak_log")
                            setBlock(startX+11, j, startZ+11, "oak_log")   

                        if connectingCells[0]:
                            #Doorway
                            setBlock(startX+7, h+1, startZ+4, "air")
                            setBlock(startX+7, h+2, startZ+4, "air")
                            setBlock(startX+8, h+2, startZ+4, "air")
                            setBlock(startX+8, h+1, startZ+4, "air")
                            #setBlock(startX+7, h+1, startZ+4, "jungle_door")
                            #setBlock(startX+8, h+1, startZ+4, "jungle_door")
                            #setBlock(startX+7, h+2, startZ+4, "jungle_door")
                            #setBlock(startX+8, h+2, startZ+4, "jungle_door")
                            #Window
                            setBlock(startX+4, h+2, startZ+7, "glass")
                            setBlock(startX+4, h+2, startZ+8, "glass")
                            #Bookcase
                            setBlock(startX+10, h+1, startZ+6, "bookshelf")
                            setBlock(startX+10, h+1, startZ+7, "bookshelf")
                            setBlock(startX+10, h+2, startZ+6, "bookshelf")
                            setBlock(startX+10, h+2, startZ+7, "bookshelf")
                            #EnchantingCorner
                            setBlock(startX+10, h+1, startZ+10, "enchanting_table")
                            setBlock(startX+10, h+3, startZ+10, "soul_lantern")
                            #Lights
                            #setBlock(startX+6, h+2, startZ+5, "wall_torch")
                            #setBlock(startX+9, h+2, startZ+5, "wall_torch")
                            setBlock(startX+5, h+1, startZ+5, "glowstone")
                            setBlock(startX+10, h+1, startZ+5, "glowstone")
                            #Crafting
                            setBlock(startX+5, h+1, startZ+7, "crafting_table")
                            setBlock(startX+5, h+1, startZ+8, "furnace")
                            #Garden
                            setBlock(startX+3, h, startZ+6, "farmland")
                            setBlock(startX+3, h, startZ+7, "farmland")
                            setBlock(startX+3, h, startZ+8, "farmland")
                            setBlock(startX+3, h, startZ+9, "farmland")
                            setBlock(startX+3, h+1, startZ+5, "dark_oak_slab")
                            setBlock(startX+3, h+1, startZ+10, "dark_oak_slab")
                            setBlock(startX+2, h+1, startZ+5, "dark_oak_slab")
                            setBlock(startX+2, h+1, startZ+6, "dark_oak_slab")
                            setBlock(startX+2, h+1, startZ+7, "dark_oak_slab")
                            setBlock(startX+2, h+1, startZ+8, "dark_oak_slab")
                            setBlock(startX+2, h+1, startZ+9, "dark_oak_slab")
                            setBlock(startX+2, h+1, startZ+10, "dark_oak_slab")
                            setBlock(startX+3, h+1, startZ+6, "red_tulip")
                            setBlock(startX+3, h+1, startZ+7, "red_tulip")
                            setBlock(startX+3, h+1, startZ+8, "red_tulip")
                            setBlock(startX+3, h+1, startZ+9, "red_tulip")
                        elif connectingCells[1]:
                            #Doorway
                            setBlock(startX+4, h+1, startZ+7, "air")
                            setBlock(startX+4, h+2, startZ+7, "air")
                            setBlock(startX+4, h+2, startZ+8, "air")
                            setBlock(startX+4, h+1, startZ+8, "air")
                            #setBlock(startX+7, h+1, startZ+4, "jungle_door")
                            #setBlock(startX+8, h+1, startZ+4, "jungle_door")
                            #setBlock(startX+7, h+2, startZ+4, "jungle_door")
                            #setBlock(startX+8, h+2, startZ+4, "jungle_door")
                            #Window
                            setBlock(startX+8, h+2, startZ+4, "glass")
                            setBlock(startX+8, h+2, startZ+4, "glass")
                            #Bookcase
                            setBlock(startX+6, h+1, startZ+10, "bookshelf")
                            setBlock(startX+7, h+1, startZ+10, "bookshelf")
                            setBlock(startX+6, h+2, startZ+10, "bookshelf")
                            setBlock(startX+7, h+2, startZ+10, "bookshelf")
                            #EnchantingCorner
                            setBlock(startX+10, h+1, startZ+10, "enchanting_table")
                            setBlock(startX+10, h+3, startZ+10, "soul_lantern")
                            #Lights
                            #setBlock(startX+6, h+2, startZ+5, "wall_torch")
                            #setBlock(startX+9, h+2, startZ+5, "wall_torch")
                            setBlock(startX+5, h+1, startZ+5, "glowstone")
                            setBlock(startX+5, h+1, startZ+10, "glowstone")
                            #Crafting
                            setBlock(startX+7, h+1, startZ+5, "crafting_table")
                            setBlock(startX+8, h+1, startZ+5, "furnace")
                            #Garden
                            setBlock(startX+6, h, startZ+3, "farmland")
                            setBlock(startX+7, h, startZ+3, "farmland")
                            setBlock(startX+8, h, startZ+3, "farmland")
                            setBlock(startX+9, h, startZ+3, "farmland")
                            setBlock(startX+5, h+1, startZ+3, "dark_oak_slab")
                            setBlock(startX+10, h+1, startZ+3, "dark_oak_slab")
                            setBlock(startX+5, h+1, startZ+2, "dark_oak_slab")
                            setBlock(startX+6, h+1, startZ+2, "dark_oak_slab")
                            setBlock(startX+7, h+1, startZ+2, "dark_oak_slab")
                            setBlock(startX+8, h+1, startZ+2, "dark_oak_slab")
                            setBlock(startX+9, h+1, startZ+2, "dark_oak_slab")
                            setBlock(startX+10, h+1, startZ+2, "dark_oak_slab")
                            setBlock(startX+6, h+1, startZ+3, "red_tulip")
                            setBlock(startX+7, h+1, startZ+3, "red_tulip")
                            setBlock(startX+8, h+1, startZ+3, "red_tulip")
                            setBlock(startX+9, h+1, startZ+3, "red_tulip")
                        elif connectingCells[2]:
                            #Doorway
                            setBlock(startX+8, h+1, startZ+11, "air")
                            setBlock(startX+8, h+2, startZ+11, "air")
                            setBlock(startX+7, h+2, startZ+11, "air")
                            setBlock(startX+7, h+1, startZ+11, "air")
                            #setBlock(startX+7, h+1, startZ+4, "jungle_door")
                            #setBlock(startX+8, h+1, startZ+4, "jungle_door")
                            #setBlock(startX+7, h+2, startZ+4, "jungle_door")
                            #setBlock(startX+8, h+2, startZ+4, "jungle_door")
                            #Window
                            setBlock(startX+11, h+2, startZ+8, "glass")
                            setBlock(startX+11, h+2, startZ+7, "glass")
                            #Bookcase
                            setBlock(startX+5, h+1, startZ+9, "bookshelf")
                            setBlock(startX+5, h+1, startZ+8, "bookshelf")
                            setBlock(startX+5, h+2, startZ+9, "bookshelf")
                            setBlock(startX+5, h+2, startZ+8, "bookshelf")
                            #EnchantingCorner
                            setBlock(startX+5, h+1, startZ+5, "enchanting_table")
                            setBlock(startX+5, h+3, startZ+5, "soul_lantern")
                            #Lights
                            #setBlock(startX+6, h+2, startZ+5, "wall_torch")
                            #setBlock(startX+9, h+2, startZ+5, "wall_torch")
                            setBlock(startX+10, h+1, startZ+10, "glowstone")
                            setBlock(startX+5, h+1, startZ+10, "glowstone")
                            #Crafting
                            setBlock(startX+10, h+1, startZ+8, "crafting_table")
                            setBlock(startX+10, h+1, startZ+7, "furnace")
                            #Garden
                            setBlock(startX+12, h, startZ+9, "farmland")
                            setBlock(startX+12, h, startZ+8, "farmland")
                            setBlock(startX+12, h, startZ+7, "farmland")
                            setBlock(startX+12, h, startZ+6, "farmland")
                            setBlock(startX+12, h+1, startZ+10, "dark_oak_slab")
                            setBlock(startX+12, h+1, startZ+5, "dark_oak_slab")
                            setBlock(startX+13, h+1, startZ+10, "dark_oak_slab")
                            setBlock(startX+13, h+1, startZ+9, "dark_oak_slab")
                            setBlock(startX+13, h+1, startZ+8, "dark_oak_slab")
                            setBlock(startX+13, h+1, startZ+7, "dark_oak_slab")
                            setBlock(startX+13, h+1, startZ+6, "dark_oak_slab")
                            setBlock(startX+13, h+1, startZ+5, "dark_oak_slab")
                            setBlock(startX+12, h+1, startZ+9, "red_tulip")
                            setBlock(startX+12, h+1, startZ+8, "red_tulip")
                            setBlock(startX+12, h+1, startZ+7, "red_tulip")
                            setBlock(startX+12, h+1, startZ+6, "red_tulip")
                        elif connectingCells[3]:
                            #Doorway
                            setBlock(startX+11, h+1, startZ+8, "air")
                            setBlock(startX+11, h+2, startZ+8, "air")
                            setBlock(startX+11, h+2, startZ+7, "air")
                            setBlock(startX+11, h+1, startZ+7, "air")
                            #setBlock(startX+7, h+1, startZ+4, "jungle_door")
                            #setBlock(startX+8, h+1, startZ+4, "jungle_door")
                            #setBlock(startX+7, h+2, startZ+4, "jungle_door")
                            #setBlock(startX+8, h+2, startZ+4, "jungle_door")
                            #Window
                            setBlock(startX+8, h+2, startZ+11, "glass")
                            setBlock(startX+7, h+2, startZ+11, "glass")
                            #Bookcase
                            setBlock(startX+9, h+1, startZ+5, "bookshelf")
                            setBlock(startX+8, h+1, startZ+5, "bookshelf")
                            setBlock(startX+9, h+2, startZ+5, "bookshelf")
                            setBlock(startX+8, h+2, startZ+5, "bookshelf")
                            #EnchantingCorner
                            setBlock(startX+5, h+1, startZ+5, "enchanting_table")
                            setBlock(startX+5, h+3, startZ+5, "soul_lantern")
                            #Lights
                            #setBlock(startX+6, h+2, startZ+5, "wall_torch")
                            #setBlock(startX+9, h+2, startZ+5, "wall_torch")
                            setBlock(startX+10, h+1, startZ+10, "glowstone")
                            setBlock(startX+10, h+1, startZ+5, "glowstone")
                            #Crafting
                            setBlock(startX+8, h+1, startZ+10, "crafting_table")
                            setBlock(startX+7, h+1, startZ+10, "furnace")
                            #Garden
                            setBlock(startX+9, h, startZ+12, "farmland")
                            setBlock(startX+8, h, startZ+12, "farmland")
                            setBlock(startX+7, h, startZ+12, "farmland")
                            setBlock(startX+6, h, startZ+12, "farmland")
                            setBlock(startX+10, h+1, startZ+12, "dark_oak_slab")
                            setBlock(startX+5, h+1, startZ+12, "dark_oak_slab")
                            setBlock(startX+10, h+1, startZ+13, "dark_oak_slab")
                            setBlock(startX+9, h+1, startZ+13, "dark_oak_slab")
                            setBlock(startX+8, h+1, startZ+13, "dark_oak_slab")
                            setBlock(startX+7, h+1, startZ+13, "dark_oak_slab")
                            setBlock(startX+6, h+1, startZ+13, "dark_oak_slab")
                            setBlock(startX+5, h+1, startZ+13, "dark_oak_slab")
                            setBlock(startX+9, h+1, startZ+12, "red_tulip")
                            setBlock(startX+8, h+1, startZ+12, "red_tulip")
                            setBlock(startX+7, h+1, startZ+12, "red_tulip")
                            setBlock(startX+6, h+1, startZ+12, "red_tulip")
                        if connectingCells[0]:
                            setBlock(startX+7, h+1, startZ, "air")
                            setBlock(startX+8, h+1, startZ, "air")
                        if connectingCells[1]:
                            setBlock(startX, h+1, startZ+7, "air")
                            setBlock(startX, h+1, startZ+8, "air")
                        if connectingCells[2]:
                            setBlock(startX+7, h+1, startZ+15, "air")
                            setBlock(startX+8, h+1, startZ+15, "air")
                        if connectingCells[3]:
                            setBlock(startX+15, h+1, startZ+7, "air")
                            setBlock(startX+15, h+1, startZ+8  , "air")


                    #Manor
                    elif self.grid[x][z].identifier == 4:
                        return

                    #Somethin
                    elif self.grid[x][z].identifier == 5:
                        return

                    #Castle
                    elif self.grid[x][z].identifier == 6:
                        return

class Cell:
    def __init__(self, identifier=0, visited=False):
        self.identifier = identifier
        self.visited = visited
        self.edges = []

    def __str__(self):
        string = "Identifier: " + str(self.identifier) + "\nEdges: \n"
        for i in range(len(self.edges)):
            string += str(self.edges[i]) + "\n"
        return string

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

grid = Grid(area, 16)
grid.populate(15)
grid.checkMountains()
print(grid)
grid.getEdges(1000)
edges = grid.mst()
grid.pathify(edges)
print(grid)
grid.build()
#for i in range(len(edges)):
#    print(edges[i])
