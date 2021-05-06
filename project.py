#Tyson Hickey
#tjh557@mun.ca
#201507225

import time
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

#Function which helps mst by getting rid of useless or duplicate paths 
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

#area - stores given area
#division - how many minecraft blocks each cell will contain
class Grid:
    def __init__(self, area, division):
        self.area = area
        self.division = division
        self.grid = [[Cell() for x in range(int(area[2]/division))] for y in range(int(area[3]/division))]

    #Displays grid in easily readable way
    #Cells have different numbers as identifiers
    # 0 == Blank Cell
    # 1 == Path
    # 2 == Blocked Cell
    # 3 onward == Structures
    def __str__(self):
        string = "Grid: \n"
        for z in range(len(self.grid[0])):
            string += "[ "
            for x in range(len(self.grid)):
                string += str(self.grid[x][z].identifier) + " "
            string += "]\n"
        return string

    #Function helper for populate
    #It counts the neighbours and returns the number
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

    #Similar to getNeighbours but this function returns a boolean list for which cells the neighbours are in 
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

    #This function is what places the structures
    #It mainly has two ways it works, the first is by just assigning a chance a structure will spawn
    #The second uses a cellular automata to produce clusters of structures
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


    #This function looks through all of the cells to find out if there are any big obstructions such as a cliff
    #If it finds such a obstruction it sets the cell identifier to 2 and therefore blocks it from use
    def checkMountains(self, limit=2):

        #Randomly set obstructions for testing purposes
        #for z in range(len(self.grid[0])):
        #    for x in range(len(self.grid)):
        #        rand = random.randint(1, 100)
        #        if rand <= 35 and self.grid[x][z].identifier != 3:
        #            self.grid[x][z].identifier = 2
        #return


        for z in range(len(self.grid[0])):
            for x in range(len(self.grid)):
                heights = []
                startX = self.area[0] + x*self.division
                startZ = self.area[1] + z*self.division
                for i in range(startX, startX+16):
                    for j in range(startZ, startZ+16):
                        if (not getBlock(i, heightAt(i, j)-1, j) in treeList):
                            heights.append(heightAt(i, j))
                heights = sorted(heights)
                if abs(heights[-1]-heights[0]) > limit:
                    self.grid[x][z].identifier = 2

    #Helper function to getEdges(BFS)
    #Gets other cells in grid which cell in questions wants to find path to
    #Add those cells to a list and returns it
    def getOtherCells(self, _x, _z):
        cells = []
        for z in range(len(self.grid[0])):
            for x in range(len(self.grid)):
                if self.grid[x][z].identifier == 3 and (x != _x or z != _z):
                    cells.append([x, z])
        return cells

    #This is the function that finds the optimal paths from one cell to another
    #It uses BFS to spread out from the initial cell and find paths
    #There is a limit function which you can set for how many paths to find
    #If you leave it empty it will find all paths which can be very space and time consuming
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

    #Helper function to mst function
    #It checks if all cells have been visited ie a path to all cells
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

    #Function that sets neighbours to a cell as visited
    #If used there will only be paths to clusters of houses rather than a path to every house
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
            
    #Function for setting a cell as visited
    #Used in mst function
    def setVisited(self, edge):
        x = edge[0][0]
        x2 = edge[-1][0]
        z = edge[0][1]
        z2 = edge[-1][1]
        self.grid[x][z].visited = True
        self.grid[x2][z2].visited = True
        self.setNeighboursVisited(x, z)
        self.setNeighboursVisited(x2, z2)
    
    #Function which was to produce a mst
    #It does not however produce a mst
    #Very similarly to Kruskals MST however it takes from a list the best edge (shortest path)
    #It then check for a certain condition and if it fails the edge is thrown away
    #This continues until all cells are visited
    #I tried using a DFS to check for cycles but was unsuccesful so i resorted to visiting all nodes instead
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

    #Simple function which takes a list of cells and sets them as a path 
    def pathify(self, edges):
        for i in range(len(edges)):
            for j in range(1, len(edges[i])-1):
                self.grid[edges[i][j][0]][edges[i][j][1]].identifier = 1

    #This function uses random numbers to assign structure identifiers by varying chance
    def setBuildings(self):
        for z in range(len(self.grid[0])):
            for x in range(len(self.grid)):
                if self.grid[x][z].identifier == 3:
                    rand = random.randint(1, 100)
                    if rand <= 20:
                        self.grid[x][z].identifier = 4
                    elif rand <= 40:
                        self.grid[x][z].identifier = 5
                    elif rand <= 50:
                        self.grid[x][z].identifier = 6
                    else:
                        self.grid[x][z].identifier = 3

    #This function attempts to find the best height for a cell and change all blocks within to this height
    #It does this by getting the height of all blocks in the cell and then taking the mode of that list
    #When it has that it attempts to change all the blocks to that height in the cell
    #Also it was going to remove trees but as that has 3 layers to iterate through it takes too long and is very buggy
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
                    if block == "minecraft:water" or block == "minecraft:sand":
                        block = "dirt"
                    while(height != h):
                        #print(block)
                        setBlock(i, height, j, block)
                        height += 1
        #for j in range(h, h+10):
        #    for i in range(x, x+16):
        #        for k in range(z, z+16):
        #            if getBlock(i, j, k) in treeList:
        #                setBlock(i, j, k, "air")
        return h

#MOST OF THE REMAINING CODE IS FOR PLACEMENT OF BLOCKS
#Class for Cell at bottom
#It does attempt somethings such as always facing the buildings towards either a path or another building
#It does that with the returnNeighbours function from earlier
#After that I coded the all the static blocks and then 4 versions of the blocks that would change via where the structure was facing
    def build(self):
        for z in range(len(self.grid[0])):
            for x in range(len(self.grid)):
                if self.grid[x][z].identifier != 0 and self.grid[x][z].identifier != 2:
                    #NORTH>WEST>SOUTH>EAST
                    connectingCells = self.returnNeighbours(x, z)
                    startX = self.area[0] + x*self.division
                    startZ = self.area[1] + z*self.division
                    endX = self.area[0] + x*self.division + self.division
                    endZ = self.area[1] + z*self.division + self.division
                    h = self.level(startX, startZ)

############################################BUILDING#################################################
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

                    #Places bedrock for testing purposes            
                    #elif self.grid[x][z].identifier == 2:
                    #    for i in range(startX, endX):
                    #        for j in range(startZ, endZ):
                    #            setBlock(i, heightAt(i, j), j, "bedrock")

                    #Cabin
                    elif self.grid[x][z].identifier == 3:
                        for i in range(startX, startX+16):
                            for j in range(startZ, startZ+16):
                                setBlock(i, h, j, "dirt")
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
                        else:
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
                        for i in range(startX, startX+16):
                            for j in range(startZ, startZ+16):
                                setBlock(i, h, j, "dirt")
                        for i in range(startX, startX+16):
                            setBlock(i, h+1, startZ, "oak_fence")
                            setBlock(i, h+1, startZ+15, "oak_fence")
                        for j in range(startZ, startZ+16):
                            setBlock(startX, h+1, j, "oak_fence")
                            setBlock(startX+15, h+1, j, "oak_fence")
                        for i in range(startX+3, startX+13):
                            for k in range(startZ+3, startZ+13):
                                setBlock(i, h, k, "oak_planks")
                                setBlock(i, h+4, k, "oak_planks")
                                setBlock(i, h+8, k, "oak_planks")
                        for j in range(h+1, h+8):
                            for i in range(startX+3, startX+13):
                                setBlock(i, j, startZ+3, "oak_planks")
                                setBlock(i, j, startZ+12, "oak_planks")
                            for k in range(startZ+3, startZ+13):
                                setBlock(startX+3, j, k, "oak_planks")
                                setBlock(startX+12, j, k, "oak_planks")
                        if connectingCells[0]:
                            #Doors
                            setBlock(startX+7, h+1, startZ+3, "air")
                            setBlock(startX+8, h+1, startZ+3, "air")
                            setBlock(startX+7, h+2, startZ+3, "air")
                            setBlock(startX+8, h+2, startZ+3, "air")
                            #Balcony
                            setBlock(startX+6, h+1, startZ+2, "oak_fence")
                            setBlock(startX+6, h+2, startZ+2, "oak_fence")
                            setBlock(startX+9, h+1, startZ+2, "oak_fence")
                            setBlock(startX+9, h+2, startZ+2, "oak_fence")
                            setBlock(startX+6, h+3, startZ+2, "oak_planks")
                            setBlock(startX+7, h+3, startZ+2, "oak_planks")
                            setBlock(startX+8, h+3, startZ+2, "oak_planks")
                            setBlock(startX+9, h+3, startZ+2, "oak_planks")
                            setBlock(startX+6, h+4, startZ+2, "oak_fence")
                            setBlock(startX+7, h+4, startZ+2, "oak_fence")
                            setBlock(startX+8, h+4, startZ+2, "oak_fence")
                            setBlock(startX+9, h+4, startZ+2, "oak_fence")
                            for j in range(h+4, h+8):
                                for i in range(startX+6, startX+10):
                                    setBlock(i, j, startZ+3, "air")
                            setBlock(startX+6, h+4, startZ+4, "oak_planks")
                            setBlock(startX+6, h+5, startZ+4, "oak_planks")
                            setBlock(startX+6, h+6, startZ+4, "oak_planks")
                            setBlock(startX+6, h+7, startZ+4, "oak_planks")
                            setBlock(startX+7, h+4, startZ+4, "oak_slab")
                            setBlock(startX+8, h+4, startZ+4, "oak_slab")
                            setBlock(startX+7, h+7, startZ+4, "oak_planks")
                            setBlock(startX+8, h+7, startZ+4, "oak_planks")
                            setBlock(startX+9, h+4, startZ+4, "oak_planks")
                            setBlock(startX+9, h+5, startZ+4, "oak_planks")
                            setBlock(startX+9, h+6, startZ+4, "oak_planks")
                            setBlock(startX+9, h+7, startZ+4, "oak_planks")
                            #Stairs
                            setBlock(startX+5, h+1, startZ+10, "oak_planks")
                            setBlock(startX+5, h+1, startZ+11, "oak_planks")
                            setBlock(startX+4, h+1, startZ+9, "oak_planks")
                            setBlock(startX+4, h+1, startZ+8, "oak_planks")
                            setBlock(startX+4, h+2, startZ+8, "oak_planks")
                            setBlock(startX+4, h+2, startZ+9, "oak_planks")
                            setBlock(startX+4, h+2, startZ+10, "oak_planks")
                            setBlock(startX+4, h+2, startZ+11, "oak_planks")
                            setBlock(startX+4, h+3, startZ+8, "oak_planks")
                            setBlock(startX+4, h+3, startZ+9, "oak_planks")
                            setBlock(startX+5, h+1, startZ+9, "oak_slab")
                            setBlock(startX+5, h+2, startZ+11, "oak_slab")
                            setBlock(startX+4, h+3, startZ+10, "oak_slab")
                            setBlock(startX+4, h+4, startZ+8, "oak_slab")
                            setBlock(startX+4, h+4, startZ+9, "air")
                            setBlock(startX+4, h+4, startZ+10, "air")
                            setBlock(startX+4, h+4, startZ+11, "air")
                            setBlock(startX+5, h+4, startZ+9, "air")
                            setBlock(startX+5, h+4, startZ+10, "air")
                            setBlock(startX+5, h+4, startZ+11, "air")
                            #Decorations
                            setBlock(startX+10, h+5, startZ+4, "chest")
                            setBlock(startX+11, h+5, startZ+4, "chest")
                            setBlock(startX+4, h+7, startZ+4, "glowstone")
                            setBlock(startX+4, h+7, startZ+11, "glowstone")
                            setBlock(startX+11, h+7, startZ+4, "glowstone")
                            setBlock(startX+11, h+7, startZ+11, "glowstone")
                            setBlock(startX+11, h+5, startZ+11, "jukebox")
                            setBlock(startX+9, h+5, startZ+7, "light_gray_wool")
                            setBlock(startX+9, h+5, startZ+8, "light_gray_wool")
                            setBlock(startX+10, h+5, startZ+7, "light_gray_wool")
                            setBlock(startX+10, h+5, startZ+8, "light_gray_wool")
                            setBlock(startX+11, h+5, startZ+7, "dark_oak_planks")
                            setBlock(startX+11, h+5, startZ+8, "dark_oak_planks")
                            setBlock(startX+11, h+6, startZ+7, "dark_oak_planks")
                            setBlock(startX+11, h+6, startZ+8, "dark_oak_planks")
                            setBlock(startX+7, h+8, startZ+6, "glass")
                            setBlock(startX+8, h+8, startZ+6, "glass")
                            setBlock(startX+7, h+8, startZ+7, "glass")
                            setBlock(startX+8, h+8, startZ+7, "glass")
                            setBlock(startX+7, h+8, startZ+8, "glass")
                            setBlock(startX+8, h+8, startZ+8, "glass")
                            setBlock(startX+7, h+8, startZ+9, "glass")
                            setBlock(startX+8, h+8, startZ+9, "glass")
                            setBlock(startX+11, h+1, startZ+6, "crafting_table")
                            setBlock(startX+11, h+1, startZ+7, "furnace")
                            setBlock(startX+11, h+1, startZ+8, "fletching_table")
                            setBlock(startX+11, h+1, startZ+9, "smithing_table")
                            setBlock(startX+4, h+1, startZ+4, "cartography_table")
                            setBlock(startX+4, h+3, startZ+7, "glowstone")
                            setBlock(startX+11, h+3, startZ+4, "glowstone")
                            setBlock(startX+11, h+3, startZ+11, "glowstone")
                            setBlock(startX+12, h+2, startZ+7, "glass")
                            setBlock(startX+12, h+2, startZ+8, "glass")
                            
                            
                        elif connectingCells[1]:
                            #Doors
                            setBlock(startX+3, h+1, startZ+7, "air")
                            setBlock(startX+3, h+1, startZ+8, "air")
                            setBlock(startX+3, h+2, startZ+7, "air")
                            setBlock(startX+3, h+2, startZ+8, "air")
                            #Balcony
                            setBlock(startX+2, h+1, startZ+6, "oak_fence")
                            setBlock(startX+2, h+2, startZ+6, "oak_fence")
                            setBlock(startX+2, h+1, startZ+9, "oak_fence")
                            setBlock(startX+2, h+2, startZ+9, "oak_fence")
                            setBlock(startX+2, h+3, startZ+6, "oak_planks")
                            setBlock(startX+2, h+3, startZ+7, "oak_planks")
                            setBlock(startX+2, h+3, startZ+8, "oak_planks")
                            setBlock(startX+2, h+3, startZ+9, "oak_planks")
                            setBlock(startX+2, h+4, startZ+6, "oak_fence")
                            setBlock(startX+2, h+4, startZ+7, "oak_fence")
                            setBlock(startX+2, h+4, startZ+8, "oak_fence")
                            setBlock(startX+2, h+4, startZ+9, "oak_fence")
                            for j in range(h+4, h+8):
                                for k in range(startZ+6, startZ+10):
                                    setBlock(startX+3, j, k, "air")
                            setBlock(startX+4, h+4, startZ+6, "oak_planks")
                            setBlock(startX+4, h+5, startZ+6, "oak_planks")
                            setBlock(startX+4, h+6, startZ+6, "oak_planks")
                            setBlock(startX+4, h+7, startZ+6, "oak_planks")
                            setBlock(startX+4, h+4, startZ+7, "oak_slab")
                            setBlock(startX+4, h+4, startZ+8, "oak_slab")
                            setBlock(startX+4, h+7, startZ+7, "oak_planks")
                            setBlock(startX+4, h+7, startZ+8, "oak_planks")
                            setBlock(startX+4, h+4, startZ+9, "oak_planks")
                            setBlock(startX+4, h+5, startZ+9, "oak_planks")
                            setBlock(startX+4, h+6, startZ+9, "oak_planks")
                            setBlock(startX+4, h+7, startZ+9, "oak_planks")
                            #Stairs
                            setBlock(startX+10, h+1, startZ+5, "oak_planks")
                            setBlock(startX+11, h+1, startZ+5, "oak_planks")
                            setBlock(startX+9, h+1, startZ+4, "oak_planks")
                            setBlock(startX+8, h+1, startZ+4, "oak_planks")
                            setBlock(startX+8, h+2, startZ+4, "oak_planks")
                            setBlock(startX+9, h+2, startZ+4, "oak_planks")
                            setBlock(startX+10, h+2, startZ+4, "oak_planks")
                            setBlock(startX+11, h+2, startZ+4, "oak_planks")
                            setBlock(startX+8, h+3, startZ+4, "oak_planks")
                            setBlock(startX+9, h+3, startZ+4, "oak_planks")
                            setBlock(startX+9, h+1, startZ+5, "oak_slab")
                            setBlock(startX+11, h+2, startZ+5, "oak_slab")
                            setBlock(startX+10, h+3, startZ+4, "oak_slab")
                            setBlock(startX+8, h+4, startZ+4, "oak_slab")
                            setBlock(startX+9, h+4, startZ+4, "air")
                            setBlock(startX+10, h+4, startZ+4, "air")
                            setBlock(startX+11, h+4, startZ+4, "air")
                            setBlock(startX+9, h+4, startZ+5, "air")
                            setBlock(startX+10, h+4, startZ+5, "air")
                            setBlock(startX+11, h+4, startZ+5, "air")
                            #Decorations
                            setBlock(startX+4, h+5, startZ+10, "chest")
                            setBlock(startX+4, h+5, startZ+11, "chest")
                            setBlock(startX+4, h+7, startZ+4, "glowstone")
                            setBlock(startX+11, h+7, startZ+4, "glowstone")
                            setBlock(startX+4, h+7, startZ+11, "glowstone")
                            setBlock(startX+11, h+7, startZ+11, "glowstone")
                            setBlock(startX+11, h+5, startZ+11, "jukebox")
                            setBlock(startX+7, h+5, startZ+9, "light_gray_wool")
                            setBlock(startX+8, h+5, startZ+9, "light_gray_wool")
                            setBlock(startX+7, h+5, startZ+10, "light_gray_wool")
                            setBlock(startX+8, h+5, startZ+10, "light_gray_wool")
                            setBlock(startX+7, h+5, startZ+11, "dark_oak_planks")
                            setBlock(startX+8, h+5, startZ+11, "dark_oak_planks")
                            setBlock(startX+7, h+6, startZ+11, "dark_oak_planks")
                            setBlock(startX+8, h+6, startZ+11, "dark_oak_planks")
                            setBlock(startX+6, h+8, startZ+7, "glass")
                            setBlock(startX+6, h+8, startZ+8, "glass")
                            setBlock(startX+7, h+8, startZ+7, "glass")
                            setBlock(startX+7, h+8, startZ+8, "glass")
                            setBlock(startX+8, h+8, startZ+7, "glass")
                            setBlock(startX+8, h+8, startZ+8, "glass")
                            setBlock(startX+9, h+8, startZ+7, "glass")
                            setBlock(startX+9, h+8, startZ+8, "glass")
                            setBlock(startX+6, h+1, startZ+11, "crafting_table")
                            setBlock(startX+7, h+1, startZ+11, "furnace")
                            setBlock(startX+8, h+1, startZ+11, "fletching_table")
                            setBlock(startX+9, h+1, startZ+11, "smithing_table")
                            setBlock(startX+4, h+1, startZ+4, "cartography_table")
                            setBlock(startX+7, h+3, startZ+4, "glowstone")
                            setBlock(startX+4, h+3, startZ+11, "glowstone")
                            setBlock(startX+11, h+3, startZ+11, "glowstone")
                            setBlock(startX+7, h+2, startZ+12, "glass")
                            setBlock(startX+8, h+2, startZ+12, "glass")

                        elif connectingCells[2]:
                            #Doors
                            setBlock(startX+7, h+1, startZ+12, "air")
                            setBlock(startX+8, h+1, startZ+12, "air")
                            setBlock(startX+7, h+2, startZ+12, "air")
                            setBlock(startX+8, h+2, startZ+12, "air")
                            #Balcony
                            setBlock(startX+9, h+1, startZ+13, "oak_fence")
                            setBlock(startX+9, h+2, startZ+13, "oak_fence")
                            setBlock(startX+6, h+1, startZ+13, "oak_fence")
                            setBlock(startX+6, h+2, startZ+13, "oak_fence")
                            setBlock(startX+9, h+3, startZ+13, "oak_planks")
                            setBlock(startX+8, h+3, startZ+13, "oak_planks")
                            setBlock(startX+7, h+3, startZ+13, "oak_planks")
                            setBlock(startX+6, h+3, startZ+13, "oak_planks")
                            setBlock(startX+9, h+4, startZ+13, "oak_fence")
                            setBlock(startX+8, h+4, startZ+13, "oak_fence")
                            setBlock(startX+7, h+4, startZ+13, "oak_fence")
                            setBlock(startX+6, h+4, startZ+13, "oak_fence")
                            for j in range(h+4, h+8):
                                for i in range(startX+6, startX+10):
                                    setBlock(i, j, startZ+12, "air")
                            setBlock(startX+6, h+4, startZ+11, "oak_planks")
                            setBlock(startX+6, h+5, startZ+11, "oak_planks")
                            setBlock(startX+6, h+6, startZ+11, "oak_planks")
                            setBlock(startX+6, h+7, startZ+11, "oak_planks")
                            setBlock(startX+7, h+4, startZ+11, "oak_slab")
                            setBlock(startX+8, h+4, startZ+11, "oak_slab")
                            setBlock(startX+7, h+7, startZ+11, "oak_planks")
                            setBlock(startX+8, h+7, startZ+11, "oak_planks")
                            setBlock(startX+9, h+4, startZ+11, "oak_planks")
                            setBlock(startX+9, h+5, startZ+11, "oak_planks")
                            setBlock(startX+9, h+6, startZ+11, "oak_planks")
                            setBlock(startX+9, h+7, startZ+11, "oak_planks")
                            #Stairs
                            setBlock(startX+10, h+1, startZ+5, "oak_planks")
                            setBlock(startX+10, h+1, startZ+4, "oak_planks")
                            setBlock(startX+11, h+1, startZ+6, "oak_planks")
                            setBlock(startX+11, h+1, startZ+7, "oak_planks")
                            setBlock(startX+11, h+2, startZ+7, "oak_planks")
                            setBlock(startX+11, h+2, startZ+6, "oak_planks")
                            setBlock(startX+11, h+2, startZ+5, "oak_planks")
                            setBlock(startX+11, h+2, startZ+4, "oak_planks")
                            setBlock(startX+11, h+3, startZ+7, "oak_planks")
                            setBlock(startX+11, h+3, startZ+6, "oak_planks")
                            setBlock(startX+10, h+1, startZ+6, "oak_slab")
                            setBlock(startX+10, h+2, startZ+4, "oak_slab")
                            setBlock(startX+11, h+3, startZ+5, "oak_slab")
                            setBlock(startX+11, h+4, startZ+7, "oak_slab")
                            setBlock(startX+11, h+4, startZ+6, "air")
                            setBlock(startX+11, h+4, startZ+5, "air")
                            setBlock(startX+11, h+4, startZ+4, "air")
                            setBlock(startX+10, h+4, startZ+6, "air")
                            setBlock(startX+10, h+4, startZ+5, "air")
                            setBlock(startX+10, h+4, startZ+4, "air")
                            #Decorations
                            setBlock(startX+5, h+5, startZ+11, "chest")
                            setBlock(startX+4, h+5, startZ+11, "chest")
                            setBlock(startX+11, h+7, startZ+11, "glowstone")
                            setBlock(startX+11, h+7, startZ+4, "glowstone")
                            setBlock(startX+4, h+7, startZ+11, "glowstone")
                            setBlock(startX+4, h+7, startZ+4, "glowstone")
                            setBlock(startX+4, h+5, startZ+4, "jukebox")
                            setBlock(startX+6, h+5, startZ+8, "light_gray_wool")
                            setBlock(startX+6, h+5, startZ+7, "light_gray_wool")
                            setBlock(startX+5, h+5, startZ+8, "light_gray_wool")
                            setBlock(startX+5, h+5, startZ+7, "light_gray_wool")
                            setBlock(startX+4, h+5, startZ+8, "dark_oak_planks")
                            setBlock(startX+4, h+5, startZ+7, "dark_oak_planks")
                            setBlock(startX+4, h+6, startZ+8, "dark_oak_planks")
                            setBlock(startX+4, h+6, startZ+7, "dark_oak_planks")
                            setBlock(startX+8, h+8, startZ+9, "glass")
                            setBlock(startX+7, h+8, startZ+9, "glass")
                            setBlock(startX+8, h+8, startZ+9, "glass")
                            setBlock(startX+7, h+8, startZ+9, "glass")
                            setBlock(startX+8, h+8, startZ+7, "glass")
                            setBlock(startX+7, h+8, startZ+7, "glass")
                            setBlock(startX+8, h+8, startZ+6, "glass")
                            setBlock(startX+7, h+8, startZ+6, "glass")
                            setBlock(startX+4, h+1, startZ+9, "crafting_table")
                            setBlock(startX+4, h+1, startZ+8, "furnace")
                            setBlock(startX+4, h+1, startZ+7, "fletching_table")
                            setBlock(startX+4, h+1, startZ+6, "smithing_table")
                            setBlock(startX+11, h+1, startZ+11, "cartography_table")
                            setBlock(startX+11, h+3, startZ+8, "glowstone")
                            setBlock(startX+4, h+3, startZ+11, "glowstone")
                            setBlock(startX+4, h+3, startZ+4, "glowstone")
                            setBlock(startX+3, h+2, startZ+8, "glass")
                            setBlock(startX+3, h+2, startZ+7, "glass")

                        elif connectingCells[3]:
                            #Doors
                            setBlock(startX+12, h+1, startZ+7, "air")
                            setBlock(startX+12, h+1, startZ+8, "air")
                            setBlock(startX+12, h+2, startZ+7, "air")
                            setBlock(startX+12, h+2, startZ+8, "air")
                            #Balcony
                            setBlock(startX+13, h+1, startZ+9, "oak_fence")
                            setBlock(startX+13, h+2, startZ+9, "oak_fence")
                            setBlock(startX+13, h+1, startZ+6, "oak_fence")
                            setBlock(startX+13, h+2, startZ+6, "oak_fence")
                            setBlock(startX+13, h+3, startZ+9, "oak_planks")
                            setBlock(startX+13, h+3, startZ+8, "oak_planks")
                            setBlock(startX+13, h+3, startZ+7, "oak_planks")
                            setBlock(startX+13, h+3, startZ+6, "oak_planks")
                            setBlock(startX+13, h+4, startZ+9, "oak_fence")
                            setBlock(startX+13, h+4, startZ+8, "oak_fence")
                            setBlock(startX+13, h+4, startZ+7, "oak_fence")
                            setBlock(startX+13, h+4, startZ+6, "oak_fence")
                            for j in range(h+4, h+8):
                                for k in range(startZ+6, startZ+10):
                                    setBlock(startX+12, j, k, "air")
                            setBlock(startX+11, h+4, startZ+6, "oak_planks")
                            setBlock(startX+11, h+5, startZ+6, "oak_planks")
                            setBlock(startX+11, h+6, startZ+6, "oak_planks")
                            setBlock(startX+11, h+7, startZ+6, "oak_planks")
                            setBlock(startX+11, h+4, startZ+7, "oak_slab")
                            setBlock(startX+11, h+4, startZ+8, "oak_slab")
                            setBlock(startX+11, h+7, startZ+7, "oak_planks")
                            setBlock(startX+11, h+7, startZ+8, "oak_planks")
                            setBlock(startX+11, h+4, startZ+9, "oak_planks")
                            setBlock(startX+11, h+5, startZ+9, "oak_planks")
                            setBlock(startX+11, h+6, startZ+9, "oak_planks")
                            setBlock(startX+11, h+7, startZ+9, "oak_planks")
                            #Stairs
                            setBlock(startX+5, h+1, startZ+10, "oak_planks")
                            setBlock(startX+4, h+1, startZ+10, "oak_planks")
                            setBlock(startX+6, h+1, startZ+11, "oak_planks")
                            setBlock(startX+7, h+1, startZ+11, "oak_planks")
                            setBlock(startX+7, h+2, startZ+11, "oak_planks")
                            setBlock(startX+6, h+2, startZ+11, "oak_planks")
                            setBlock(startX+5, h+2, startZ+11, "oak_planks")
                            setBlock(startX+4, h+2, startZ+11, "oak_planks")
                            setBlock(startX+7, h+3, startZ+11, "oak_planks")
                            setBlock(startX+6, h+3, startZ+11, "oak_planks")
                            setBlock(startX+6, h+1, startZ+10, "oak_slab")
                            setBlock(startX+4, h+2, startZ+10, "oak_slab")
                            setBlock(startX+5, h+3, startZ+11, "oak_slab")
                            setBlock(startX+7, h+4, startZ+11, "oak_slab")
                            setBlock(startX+6, h+4, startZ+11, "air")
                            setBlock(startX+5, h+4, startZ+11, "air")
                            setBlock(startX+4, h+4, startZ+11, "air")
                            setBlock(startX+6, h+4, startZ+10, "air")
                            setBlock(startX+5, h+4, startZ+10, "air")
                            setBlock(startX+4, h+4, startZ+10, "air")
                            #Decorations
                            setBlock(startX+11, h+5, startZ+5, "chest")
                            setBlock(startX+11, h+5, startZ+4, "chest")
                            setBlock(startX+11, h+7, startZ+11, "glowstone")
                            setBlock(startX+4, h+7, startZ+11, "glowstone")
                            setBlock(startX+11, h+7, startZ+4, "glowstone")
                            setBlock(startX+4, h+7, startZ+4, "glowstone")
                            setBlock(startX+4, h+5, startZ+4, "jukebox")
                            setBlock(startX+8, h+5, startZ+6, "light_gray_wool")
                            setBlock(startX+7, h+5, startZ+6, "light_gray_wool")
                            setBlock(startX+8, h+5, startZ+5, "light_gray_wool")
                            setBlock(startX+7, h+5, startZ+5, "light_gray_wool")
                            setBlock(startX+8, h+5, startZ+4, "dark_oak_planks")
                            setBlock(startX+7, h+5, startZ+4, "dark_oak_planks")
                            setBlock(startX+8, h+6, startZ+4, "dark_oak_planks")
                            setBlock(startX+7, h+6, startZ+4, "dark_oak_planks")
                            setBlock(startX+9, h+8, startZ+8, "glass")
                            setBlock(startX+9, h+8, startZ+7, "glass")
                            setBlock(startX+8, h+8, startZ+8, "glass")
                            setBlock(startX+8, h+8, startZ+7, "glass")
                            setBlock(startX+7, h+8, startZ+8, "glass")
                            setBlock(startX+7, h+8, startZ+7, "glass")
                            setBlock(startX+6, h+8, startZ+8, "glass")
                            setBlock(startX+6, h+8, startZ+7, "glass")
                            setBlock(startX+9, h+1, startZ+4, "crafting_table")
                            setBlock(startX+8, h+1, startZ+4, "furnace")
                            setBlock(startX+7, h+1, startZ+4, "fletching_table")
                            setBlock(startX+6, h+1, startZ+4, "smithing_table")
                            setBlock(startX+11, h+1, startZ+11, "cartography_table")
                            setBlock(startX+8, h+3, startZ+11, "glowstone")
                            setBlock(startX+11, h+3, startZ+4, "glowstone")
                            setBlock(startX+4, h+3, startZ+4, "glowstone")
                            setBlock(startX+8, h+2, startZ+3, "glass")
                            setBlock(startX+7, h+2, startZ+3, "glass")
                        else:
                            #Doors
                            setBlock(startX+12, h+1, startZ+7, "air")
                            setBlock(startX+12, h+1, startZ+8, "air")
                            setBlock(startX+12, h+2, startZ+7, "air")
                            setBlock(startX+12, h+2, startZ+8, "air")
                            #Balcony
                            setBlock(startX+13, h+1, startZ+9, "oak_fence")
                            setBlock(startX+13, h+2, startZ+9, "oak_fence")
                            setBlock(startX+13, h+1, startZ+6, "oak_fence")
                            setBlock(startX+13, h+2, startZ+6, "oak_fence")
                            setBlock(startX+13, h+3, startZ+9, "oak_planks")
                            setBlock(startX+13, h+3, startZ+8, "oak_planks")
                            setBlock(startX+13, h+3, startZ+7, "oak_planks")
                            setBlock(startX+13, h+3, startZ+6, "oak_planks")
                            setBlock(startX+13, h+4, startZ+9, "oak_fence")
                            setBlock(startX+13, h+4, startZ+8, "oak_fence")
                            setBlock(startX+13, h+4, startZ+7, "oak_fence")
                            setBlock(startX+13, h+4, startZ+6, "oak_fence")
                            for j in range(h+4, h+8):
                                for k in range(startZ+6, startZ+10):
                                    setBlock(startX+12, j, k, "air")
                            setBlock(startX+11, h+4, startZ+6, "oak_planks")
                            setBlock(startX+11, h+5, startZ+6, "oak_planks")
                            setBlock(startX+11, h+6, startZ+6, "oak_planks")
                            setBlock(startX+11, h+7, startZ+6, "oak_planks")
                            setBlock(startX+11, h+4, startZ+7, "oak_slab")
                            setBlock(startX+11, h+4, startZ+8, "oak_slab")
                            setBlock(startX+11, h+7, startZ+7, "oak_planks")
                            setBlock(startX+11, h+7, startZ+8, "oak_planks")
                            setBlock(startX+11, h+4, startZ+9, "oak_planks")
                            setBlock(startX+11, h+5, startZ+9, "oak_planks")
                            setBlock(startX+11, h+6, startZ+9, "oak_planks")
                            setBlock(startX+11, h+7, startZ+9, "oak_planks")
                            #Stairs
                            setBlock(startX+5, h+1, startZ+10, "oak_planks")
                            setBlock(startX+4, h+1, startZ+10, "oak_planks")
                            setBlock(startX+6, h+1, startZ+11, "oak_planks")
                            setBlock(startX+7, h+1, startZ+11, "oak_planks")
                            setBlock(startX+7, h+2, startZ+11, "oak_planks")
                            setBlock(startX+6, h+2, startZ+11, "oak_planks")
                            setBlock(startX+5, h+2, startZ+11, "oak_planks")
                            setBlock(startX+4, h+2, startZ+11, "oak_planks")
                            setBlock(startX+7, h+3, startZ+11, "oak_planks")
                            setBlock(startX+6, h+3, startZ+11, "oak_planks")
                            setBlock(startX+6, h+1, startZ+10, "oak_slab")
                            setBlock(startX+4, h+2, startZ+10, "oak_slab")
                            setBlock(startX+5, h+3, startZ+11, "oak_slab")
                            setBlock(startX+7, h+4, startZ+11, "oak_slab")
                            setBlock(startX+6, h+4, startZ+11, "air")
                            setBlock(startX+5, h+4, startZ+11, "air")
                            setBlock(startX+4, h+4, startZ+11, "air")
                            setBlock(startX+6, h+4, startZ+10, "air")
                            setBlock(startX+5, h+4, startZ+10, "air")
                            setBlock(startX+4, h+4, startZ+10, "air")
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

                    #fountain
                    elif self.grid[x][z].identifier == 5:
                        for i in range(startX+3, startX+13):
                            for k in range(startZ+3, startZ+13):
                                setBlock(i, h, k, "stone_bricks")
                        for i in range(startX+3, startX+13):
                            setBlock(i, h+1, startZ+3, "stone_brick_slab")
                            setBlock(i, h+1, startZ+12, "stone_brick_slab")
                        for k in range(startZ+3, startZ+13):
                            setBlock(startX+3, h+1, k, "stone_brick_slab")
                            setBlock(startX+12, h+1, k, "stone_brick_slab")
                        for i in range(startX+5, startX+11):
                            setBlock(i, h+1, startZ+5, "stone_brick_slab")
                            setBlock(i, h+1, startZ+10, "stone_brick_slab")
                        for k in range(startZ+5, startZ+10):
                            setBlock(startX+5, h+1, k, "stone_brick_slab")
                            setBlock(startX+10, h+1, k, "stone_brick_slab")
                        setBlock(startX+7, h+1, startZ+7, "stone_bricks")
                        setBlock(startX+7, h+2, startZ+7, "stone_bricks")
                        setBlock(startX+7, h+1, startZ+8, "stone_bricks")
                        setBlock(startX+7, h+2, startZ+8, "stone_bricks")
                        setBlock(startX+8, h+1, startZ+7, "stone_bricks")
                        setBlock(startX+8, h+2, startZ+7, "stone_bricks")
                        setBlock(startX+8, h+1, startZ+8, "stone_bricks")
                        setBlock(startX+8, h+2, startZ+8, "stone_bricks")
                        setBlock(startX+7, h+3, startZ+7, "water")
                        setBlock(startX+7, h+3, startZ+8, "water")
                        setBlock(startX+8, h+3, startZ+7, "water")
                        setBlock(startX+8, h+3, startZ+8, "water")

                        if connectingCells[0]:
                            setBlock(startX+7, h+1, startZ+3, "air")
                            setBlock(startX+8, h+1, startZ+3, "air")
                            for i in range(startX+6, startX+10):
                                for k in range(startZ, startZ+4):
                                    setBlock(i, h, k, "stone_bricks")
                            for k in range(startZ, startZ+4):
                                setBlock(startX+6, h+1, k, "stone_brick_slab")
                                setBlock(startX+9, h+1, k, "stone_brick_slab")
                        if connectingCells[1]:
                            setBlock(startX+3, h+1, startZ+7, "air")
                            setBlock(startX+3, h+1, startZ+8, "air")
                            for i in range(startX, startX+4):
                                for k in range(startZ+6, startZ+10):
                                    setBlock(i, h, k, "stone_bricks")
                            for i in range(startX, startX+4):
                                setBlock(i, h+1, startZ+6, "stone_brick_slab")
                                setBlock(i, h+1, startZ+9, "stone_brick_slab")
                        if connectingCells[2]:
                            setBlock(startX+8, h+1, startZ+12, "air")
                            setBlock(startX+7, h+1, startZ+12, "air")
                            for i in range(startX+6, startX+10):
                                for k in range(startZ+12, startZ+16):
                                    setBlock(i, h, k, "stone_bricks")
                            for k in range(startZ+12, startZ+16):
                                setBlock(startX+6, h+1, k, "stone_brick_slab")
                                setBlock(startX+9, h+1, k, "stone_brick_slab")
                        if connectingCells[3]:
                            setBlock(startX+12, h+1, startZ+8, "air")
                            setBlock(startX+12, h+1, startZ+7, "air")
                            for i in range(startX+12, startX+16):
                                for k in range(startZ+6, startZ+10):
                                    setBlock(i, h, k, "stone_bricks")
                            for i in range(startX+12, startX+16):
                                setBlock(i, h+1, startZ+9, "stone_brick_slab")
                                setBlock(i, h+1, startZ+6, "stone_brick_slab")

                    #Armoury
                    elif self.grid[x][z].identifier == 6:
                        for i in range(startX, startX+16):
                            for k in range(startZ, startZ+16):
                                setBlock(i, h, k, "stone_bricks")
                                setBlock(i, h+6, k, "stone_bricks")
                        for j in range(h, h+10):
                            for i in range(startX, startX+16):
                                setBlock(i, j, startZ, "stone_bricks")
                                setBlock(i, j, startZ+15, "stone_bricks")
                            for k in range(startZ, startZ+16):
                                setBlock(startX, j, k, "stone_bricks")
                                setBlock(startX+15, j, k, "stone_bricks")
                        for i in range(startX, startX+16, 2):
                            setBlock(i, h+10, startZ, "stone_bricks")
                            setBlock(i, h+10, startZ+15, "stone_bricks")
                        for k in range(startZ, startZ+16, 2):
                            setBlock(startX, h+10, k, "stone_bricks")
                            setBlock(startX+15, h+10, k, "stone_bricks")
                        setBlock(startX+1, h+5, startZ+1, "glowstone")
                        setBlock(startX+14, h+5, startZ+1, "glowstone")
                        setBlock(startX+1, h+5, startZ+14, "glowstone")
                        setBlock(startX+14, h+5, startZ+14, "glowstone")
                        if connectingCells[0]:
                            setBlock(startX+7, h+1, startZ, "red_carpet")
                            setBlock(startX+8, h+1, startZ, "red_carpet")
                            setBlock(startX+7, h+2, startZ, "air")
                            setBlock(startX+8, h+2, startZ, "air")
                            setBlock(startX+7, h+3, startZ, "iron_bars")
                            setBlock(startX+8, h+3, startZ, "iron_bars")
                            for i in range(startX+7, startX+9):
                                for k in range(startZ+1, startZ+10):
                                    setBlock(i, h+1, k, "red_carpet")
                            for i in range(startX+3, startX+15):
                                setBlock(i, h+1, startZ+10, "dark_oak_planks")
                            for i in range(startX+1, startX+14, 2):
                                setBlock(i, h+1, startZ+14, "smithing_table")
                                setBlock(i+1, h+1, startZ+14, "blast_furnace")
                            setBlock(startX+5, h+4, startZ+14, "zombie_wall_head")
                            setBlock(startX+8, h+4, startZ+14, "dragon_wall_head")
                            setBlock(startX+11, h+4, startZ+14, "creeper_wall_head")
                        elif connectingCells[1]:
                            setBlock(startX, h+1, startZ+7, "red_carpet")
                            setBlock(startX, h+1, startZ+8, "red_carpet")
                            setBlock(startX, h+2, startZ+7, "air")
                            setBlock(startX, h+2, startZ+8, "air")
                            setBlock(startX, h+3, startZ+7, "iron_bars")
                            setBlock(startX, h+3, startZ+8, "iron_bars")
                            for i in range(startX+1, startX+10):
                                for k in range(startZ+7, startZ+9):
                                    setBlock(i, h+1, k, "red_carpet")
                            for k in range(startZ+3, startZ+15):
                                setBlock(startX+10, h+1, k, "dark_oak_planks")
                            for k in range(startZ+1, startZ+14, 2):
                                setBlock(startX+14, h+1, k, "smithing_table")
                                setBlock(startX+14, h+1, k+1, "blast_furnace")
                            setBlock(startX+14, h+4, startZ+5, "zombie_wall_head")
                            setBlock(startX+14, h+4, startZ+8, "dragon_wall_head")
                            setBlock(startX+14, h+4, startZ+11, "creeper_wall_head")
                        elif connectingCells[2]:
                            setBlock(startX+7, h+1, startZ+15, "red_carpet")
                            setBlock(startX+8, h+1, startZ+15, "red_carpet")
                            setBlock(startX+7, h+2, startZ+15, "air")
                            setBlock(startX+8, h+2, startZ+15, "air")
                            setBlock(startX+7, h+3, startZ+15, "iron_bars")
                            setBlock(startX+8, h+3, startZ+15, "iron_bars")
                            for i in range(startX+7, startX+9):
                                for k in range(startZ+5, startZ+14):
                                    setBlock(i, h+1, k, "red_carpet")
                            for i in range(startX+1, startX+12):
                                setBlock(i, h+1, startZ+10, "dark_oak_planks")
                            for i in range(startX+1, startX+14, 2):
                                setBlock(i, h+1, startZ+1, "smithing_table")
                                setBlock(i+1, h+1, startZ+1, "blast_furnace")
                            setBlock(startX+10, h+4, startZ+1, "zombie_wall_head")
                            setBlock(startX+7, h+4, startZ+1, "dragon_wall_head")
                            setBlock(startX+4, h+4, startZ+1, "creeper_wall_head")
                        elif connectingCells[2]:
                            setBlock(startX+15, h+1, startZ+7, "red_carpet")
                            setBlock(startX+15, h+1, startZ+8, "red_carpet")
                            setBlock(startX+15, h+2, startZ+7, "air")
                            setBlock(startX+15, h+2, startZ+8, "air")
                            setBlock(startX+15, h+3, startZ+7, "iron_bars")
                            setBlock(startX+15, h+3, startZ+8, "iron_bars")
                            for i in range(startX+5, startX+14):
                                for k in range(startZ+7, startZ+9):
                                    setBlock(i, h+1, k, "red_carpet")
                            for k in range(startZ+1, startZ+12):
                                setBlock(startX+10, h+1, k, "dark_oak_planks")
                            for k in range(startZ+1, startZ+14, 2):
                                setBlock(startZ+1, h+1, k, "smithing_table")
                                setBlock(startZ+1, h+1, k+1, "blast_furnace")
                            setBlock(startX+1, h+4, startZ+10, "zombie_wall_head")
                            setBlock(startX+1, h+4, startZ+7, "dragon_wall_head")
                            setBlock(startX+1, h+4, startZ+4, "creeper_wall_head")

##############################################BUILDING END################################################################

#Simple class which represents the cells on the grid
#identifier - # which represents what type of cell it is (refer to grid class comment)
#visited - helpful for building paths to make sure all cells are visited
#edges - List of all edges to other structure cells.
#edge - Representes as a list of [x,z] from one structure cell to the next
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

#Places fence around area
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
grid.checkMountains(5)
print("Initial Grid:")
print(grid)
grid.getEdges(1000)
edges = grid.mst()
grid.pathify(edges)
print("Pathways created:")
print(grid)
grid.setBuildings()
grid.build()
print("Final Grid:")
print(grid)
