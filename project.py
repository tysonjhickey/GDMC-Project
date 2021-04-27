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


#Class for taking area given and dividing it up into even 10x10 areas
#Also has function for building houses on grid
class Partition:
    def __init__(self, area):
        self.__area = [math.ceil(area[0] / 10), math.ceil(area[1] / 10), int(area[2] / 10), int(area[3] / 10)]
        self.grid = [["" for x in range(self.__area[2])] for y in range(self.__area[3])]

    def __str__(self):
        string = ""
        for i in range(0, len(self.grid)):
            string += "[ "
            for j in range(0, len(self.grid[0])):
                string += str(self.grid[i][j]) + " "
            string += "]\n"
        return string

    def isUsed(self, x, z):
        x = int(x / 10)
        z = int(z / 10)
        if self.grid[x][z]:
            return True 
        return False

    def use(self, x, z, structure):
        x = int(x / 10)
        z = int(z / 10)
        self.grid[x][z] = structure

    def buildHouses(self):
        for i in range(0, len(self.grid)):
            for j in range(0, len(self.grid[0])):
                if self.grid[i][j]:
                    buildSmallHouse(i*10, j*10)

    def buildCastle(self):
        for i in range(0, len(self.grid)):
            for j in range(0, len(self.grid[0])):
                if (    
                        i+2 < len(self.grid) and
                        j+2 < len(self.grid) and
                        not self.grid[i][j] and 
                        not self.grid[i+1][j] and 
                        not self.grid[i+2][j] and
                        not self.grid[i][j+1] and
                        not self.grid[i+1][j+1] and 
                        not self.grid[i+2][j+1] and 
                        not self.grid[i][j+2] and
                        not self.grid[i+1][j+2] and
                        not self.grid[i+2][j+2]
                   ):
                        buildCastle(i*10, j*10)
                        return 
                     
                    
                            

#Gives height of x,z coordinate 
def heightAt(x, z):
    return heightmap[(x - area[0], z - area[1])]

#Gives height of first block on x, z coordinate
def blockHeightAt(x, z):
    return heightmap[(x - area[0], z - area[1])]-1

def setBlock(x, y, z, block):
    interfaceUtils.setBlock(x, y, z, block)

def getBlock(x, y, z):
    return interfaceUtils.getBlock(x, y, z)

def isWater(x, y, z):
    if getBlock(x, y, z) == "minecraft:water":
        return True
    else:
        return False

#Function for cellular automata to randomize grid
def placementGeneration(partition, aliveChance, deathLimit, birthLimit, steps):
    oldGrid = partition.grid
    newGrid = oldGrid
    for i in range(0, len(oldGrid)):
        for j in range(0, len(oldGrid[0])):
            if random.random()*100 <= aliveChance:
                oldGrid[i][j] = True
    for step in range(0, steps):
        oldGrid = newGrid
        for i in range(0, len(oldGrid)):
            for j in range(0, len(oldGrid[0])):
                nbs = 0
                if i-1 >= 0 and j-1 >=0:
                    if oldGrid[i-1][j-1]:
                        nbs += 1
                if j-1 >= 0:
                    if oldGrid[i][j-1]:
                        nbs += 1
                if i+1 < len(oldGrid) and j-1 >=0:
                    if oldGrid[i+1][j-1]:
                        nbs += 1
                if i-1 >= 0:
                    if oldGrid[i-1][j]:
                        nbs += 1
                if i+1 < len(oldGrid):
                    if oldGrid[i+1][j]:
                        nbs += 1
                if i-1 >= 0 and j+1 < len(oldGrid[0]):
                    if oldGrid[i-1][j+1]:
                        nbs += 1
                if j+1 < len(oldGrid[0]):
                    if oldGrid[i][j+1]:
                        nbs += 1
                if i+1 < len(oldGrid) and j+1 < len(oldGrid[0]):
                    if oldGrid[i+1][j+1]:
                        nbs += 1
                    if oldGrid[i][j]:
                        if nbs < deathLimit:
                            newGrid[i][j] = False
                        else:
                            newGrid[i][j] = True
                    else:
                        if nbs > birthLimit:
                            newGrid[i][j] = True
                        else:
                            newGrid[i][j] = False
        return newGrid
         
def buildSmallHouse(x, z):
    #6x5 size
   
    #Calculate average height of build area
    averageHeight = 0
    for i in range(x, x+10):
        for k in range(z, z+10):
            averageHeight += blockHeightAt(i, k)

    averageHeight = round(averageHeight / 100)

    #Making sure all blocks in build area are at least average height
    for i in range(x+2, x+8):
        for k in range(z+3, z+8):
            if (blockHeightAt(i, k) < averageHeight):
                blockHeight = blockHeightAt(i, k)
                while blockHeight != averageHeight:
                    setBlock(i, blockHeight, k, "dirt")
                    blockHeight += 1

    #Builds base of house
    for i in range(x+2, x+8):
        for j in range(averageHeight, averageHeight+4):
            for k in range(z+3, z+8):
                setBlock(i, j, k, "oak_planks")

    for i in range(x+3, x+7):
            for k in range(z+4, z+7):
                setBlock(i, averageHeight + 4, k, "oak_planks")

    for i in range(x+4, x+6):
        setBlock(i, averageHeight+5, z+5, "oak_planks")

    #Hollowing out of house
    for i in range(x+3, x+7):
        for j in range(averageHeight+1 , averageHeight+3):
            for k in range(z+4, z+7):
                setBlock(i, j, k, "air")

    facing = random.randint(0, 3)

    #Small features that could not be in loops
    if facing == 0:
        setBlock(x+2, averageHeight+1, z+5, "air")
        setBlock(x+2, averageHeight+2, z+5, "air")
        setBlock(x+4, averageHeight+2, z+3, "glass")
        setBlock(x+5, averageHeight+2, z+3, "glass")
        setBlock(x+4, averageHeight+2, z+7, "glass")
        setBlock(x+5, averageHeight+2, z+7, "glass")
    elif facing == 1:
        setBlock(x+7, averageHeight+1, z+5, "air")
        setBlock(x+7, averageHeight+2, z+5, "air")
        setBlock(x+4, averageHeight+2, z+3, "glass")
        setBlock(x+5, averageHeight+2, z+3, "glass")
        setBlock(x+4, averageHeight+2, z+7, "glass")
        setBlock(x+5, averageHeight+2, z+7, "glass")
    elif facing == 2:
        setBlock(x+4, averageHeight+1, z+7, "air")
        setBlock(x+4, averageHeight+2, z+7, "air")
        setBlock(x+5, averageHeight+1, z+7, "air")
        setBlock(x+5, averageHeight+2, z+7, "air")
        setBlock(x+2, averageHeight+2, z+5, "glass")
        setBlock(x+7, averageHeight+2, z+5, "glass")
    else:
        setBlock(x+4, averageHeight+1, z+3, "air")
        setBlock(x+4, averageHeight+2, z+3, "air")
        setBlock(x+5, averageHeight+1, z+3, "air")
        setBlock(x+5, averageHeight+2, z+3, "air")
        setBlock(x+2, averageHeight+2, z+5, "glass")
        setBlock(x+7, averageHeight+2, z+5, "glass")

def buildCastle(x, z):
    heights = []
    for i in range(x, x+30):
        for k in range(z, z+30):
            heights.append(blockHeightAt(i, k))
    
    medianHeight = int(statistics.median(heights))

    #for i in range(x, x+30):
    #    for k in range(z, z+30):
    #        if (blockHeightAt(i, k) > medianHeight):
    #            blockHeight = blockHeightAt(i, k)
    #            while (blockHeight != medianHeight):
    #                setBlock(i, blockHeight, k, "air")
    #                blockHeight -= 1
    #        elif (blockHeightAt(i, k) < medianHeight):
    #            blockHeight = blockHeightAt(i, k)
    #            while (blockHeight != medianHeight):
    #                setBlock(i, blockHeight, k, "dirt")
    #                blockHeight += 1

    for i in range(x+2, x+27):
        for k in range(z+2, z+27):
            if (blockHeightAt(i, k) < medianHeight):
                blockHeight = blockHeightAt(i, k)
                while blockHeight != medianHeight:
                    setBlock(i, blockHeight, k, "stone_bricks")
                    blockHeight += 1

    for i in range(x+2, x+27):
        for j in range(medianHeight, medianHeight+8):
            setBlock(i, j, z+2, "stone_bricks")
            setBlock(i, j, z+26, "stone_bricks")

    for k in range(z+2, z+27):
        for j in range(medianHeight, medianHeight+8):
            setBlock(x+2, j, k, "stone_bricks")
            setBlock(x+26, j, k, "stone_bricks")           

    for i in range(x+2, x+27, 2):
        setBlock(i, medianHeight+8, z+2, "stone_bricks")
        setBlock(i, medianHeight+8, z+26, "stone_bricks")

    for k in range(z+2, z+27, 2):
        setBlock(x+2, medianHeight+8, k, "stone_bricks")
        setBlock(x+26, medianHeight+8, k, "stone_bricks")
    

    

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


partition = Partition(area)
partition.grid = placementGeneration(partition, 50, 2, 5, 10)
partition.buildHouses()
partition.buildCastle()


