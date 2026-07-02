import pygame
import os
import math
import copy
import abc
import json as JSON
pygame.init()

class ImageLoading():
    def __init__(self):
        self.cachedImages = {}
        self.cachedImageSizes = {}

    def cacheImage(self,filePath):
        self.cachedImages[filePath] = pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),filePath))

    def cacheSize(self,filePath,size):
        self.cachedImageSizes[(filePath,size)] = pygame.transform.scale(self.cachedImages[filePath],size)

    def loadImage(self,filePath,size:tuple):
        if filePath not in self.cachedImages:
            self.cacheImage(filePath)
        if (filePath,size) not in self.cachedImageSizes:
            self.cacheSize(filePath,size)
        return self.cachedImageSizes[(filePath,size)]
    
imgLoading = ImageLoading()

class Utils:
    """class for any method that has nowhere else to go"""
    @staticmethod
    def getObjectOnTile(group,tilePos):
        objects = []
        for i in group:
            if i.onTile(tilePos):
                objects.append(i)
        return objects
    
    @staticmethod
    def addToGroups(object,groups,zIndex):
        for group in groups:
            group.add(object,zIndex)

    @staticmethod
    def jsonGetDictionary(fileName):
        with open(fileName,"r",encoding="utf-8") as file:
            return JSON.load(file)
        
    @staticmethod
    def addParents(parents,object):
        for i in parents:
            i.addChild(object)

class GroupCustom:
    def __init__(self):
        self.objects=[]
        self.zIndexes = {} #the order is: smaller indexes first,bigger indexes later

    def sortByzIndex(self):
        def getzIndex(object):
            return self.zIndexes[object]
        self.objects.sort(key=getzIndex)

    def add(self,object,zIndex = 0):
        self.objects.append(object)
        self.zIndexes[object] = zIndex
        self.sortByzIndex()
        
    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.objects):
            returnValue = self.objects[self.index]
            self.index += 1
            return returnValue
        else:
            raise StopIteration

class Grid:
    def __init__(self, surface: pygame.Surface,tileSize:int,groups = (),zIndex = 0):
        Utils.addToGroups(self,groups,zIndex)
        self.surface = surface
        self.surfaceSize = self.surface.get_size()
        self.tileSize = tileSize
        self.offset = [0,0]

    def getPosFromTile(self,tile: tuple):
        return tuple([axis * self.tileSize for axis in tile])
    
    def getTileFromPos(self,pos:tuple):
        pos = [pos[index]-self.offset[index] for index in range(len(pos))]  #type: ignore
        tile = [axis / self.tileSize for axis in pos]
        tile = [math.floor(i) for i in tile]
        return tile
    
    def update(self):
        if self.tileSize <= 0:
            raise Exception("grid tileSize below zero")

class Background: 
    def __init__(self,grid: Grid,image = None,groups = (),zIndex = 0):
        Utils.addToGroups(self,groups,zIndex)
        self.image = image
        self.gridRef = grid
        self.redraw()

    def redraw(self):
        self.grid = copy.copy(self.gridRef)
        self.tileSize = self.grid.tileSize
        self.surfaceSize = self.grid.surfaceSize

        self.background = pygame.Surface([self.tileSize*2+i for i in self.surfaceSize])

        tilesOnSurface = [math.ceil(axisSize/self.tileSize) for axisSize in self.background.get_size()]


        if self.image == None: 
            tile = pygame.Surface((self.tileSize,self.tileSize))
            tile.fill((255,255,255))
            pygame.draw.rect(tile,"red",pygame.Rect((0,0),(self.tileSize,self.tileSize)),int(self.tileSize/32))
        else:
            tile = imgLoading.loadImage(self.image,(self.tileSize,self.tileSize))

        for x in range(tilesOnSurface[0]):
            for y in range(tilesOnSurface[1]):
                self.background.blit(tile,self.grid.getPosFromTile((x,y))) 

    def draw(self,window):
        startPosition = self.grid.getPosFromTile((-1,-1))
        trueOffset = [i - math.floor(i/self.tileSize) * self.tileSize for i in self.gridRef.offset]
        position = [startPosition[index] + trueOffset[index] for index in range(len(startPosition))]
        window.blit(self.background,position)

class Camera:
    '''a class that simplifies interaction with Grid.offset'''
    def __init__(self,grid:Grid,initialCameraPos:tuple,groups = (), zIndex = 0):
        Utils.addToGroups(self,groups,zIndex)
        self.cameraPos = list(initialCameraPos) #camera position should always be in the center of the screeen
        self.grid = grid

    def getGlobalPos(self,localPos):
        return [localPos[index] + self.grid.offset[index] for index in range(len(localPos))]
    
    def getOffset(self):
        offset = [self.cameraPos[index] - self.grid.surfaceSize[index] / 2 for index in range(len(self.cameraPos))]
        return [i * -1 for i in offset]

    def update(self):
        self.grid.offset = self.getOffset()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.cameraPos[0] -= 10
        if keys[pygame.K_d]:
            self.cameraPos[0] += 10
        if keys[pygame.K_w]:
            self.cameraPos[1] -= 10
        if keys[pygame.K_s]:
            self.cameraPos[1] += 10

class SpritesBase:
    def __init__(self,image,x,y,width,height,groups = (),zIndex = 0):
        super().__init__()
        Utils.addToGroups(self,groups,zIndex)
        self.load(image,(width,height),(x,y))
        self.originalImage = image

    def load(self,filename,size:tuple,pos:tuple):
        self.image = imgLoading.loadImage(filename,size)
        
        self.rect = self.image.get_rect(topleft = pos)

    def draw(self,window, pos = None):
        if pos == None:
            window.blit(self.image,self.rect)
        else:
            window.blit(self.image,pos)

class Sprites(SpritesBase,abc.ABC):
    def __init__(self,image,grid: Grid,tilePos:tuple,groups: tuple = (),zIndex = 0):
        self.tilePos = list(tilePos)
        self.pos = grid.getPosFromTile(tilePos)
        size = (grid.tileSize,grid.tileSize)
        self.grid = grid 
        super().__init__(image,self.pos[0],self.pos[1],size[0],size[1],groups,zIndex)
    
    def redraw(self):
        size = (self.grid.tileSize,self.grid.tileSize)
        self.pos = self.grid.getPosFromTile(tuple(self.tilePos))
        super().load(self.originalImage,size,self.pos)

    def draw(self,window, pos=None): # pos=None is just here to remove the error
        originalPosition = [self.rect.left,self.rect.top] # type: ignore , Im too lazy to fix this
        position =[originalPosition[index]+self.grid.offset[index] for index in range(len(originalPosition))]
        super().draw(window,position)

    @abc.abstractmethod
    def onclick(self,tilePos,pos):
        '''this will be called when the player clicks'''

    def onTile(self,tilePos):
        if tilePos == self.tilePos:
            return True
        else:
            return False

class Player(Sprites):
    def onclick(self, tilePos,pos):
        if tilePos == self.tilePos:
            print("triggered")

class UISimple:
    class Base(): 
        """The base for all ui objects."""
        def __init__(self,position = [0,0],parents = [],properties = "default.json",groups = (),zIndex = 0):
            Utils.addParents(parents,self)
            Utils.addToGroups(self,groups,zIndex)
            self.size = [0,0]
            self.position = position
            self.properties = Utils.jsonGetDictionary(properties)
            self.objects = []
            self.localSurface = None
            self.propertyInit()

        def addChild(self,object):
            self.objects.append(object)

        def draw(self,surface):#optimise this entire function by caching stuff if you notice a frame drop when working with UIs
            if self.size[0] > 0 and self.size[1] > 0:
                if self.localSurface == None or self.localSurface.get_size() != self.size :
                    self.localSurface = pygame.Surface(self.size, pygame.SRCALPHA)
                self.localSurface.fill((0, 0, 0, 0)) 
                childrenPos = self.getChildrenPos()
                self.drawSelf(self.localSurface)
                for index in range(len(self.objects)):
                    self.objects[index].position = childrenPos[index]
                    self.objects[index].draw(self.localSurface)
                surface.blit(self.localSurface,self.position)

        def collisionCheck(self,pos):
            '''checks if a coordinate is in the element bounds'''
            minPos = self.position
            maxPos =   [self.position[i] + self.size[i] for i in range(2)]
            inBounds = [maxPos[i] >= pos[i] >= minPos[i] for i in range(2)]
            return inBounds[0] and inBounds[1]

        def drawSelf(self,surface):
            if self.BGcolour != None:
                surface.fill(self.BGcolour)
            if self.BGimage != None:
                surface.blit(imgLoading.loadImage(self.BGimage,surface.get_size()),(0,0))

        def update(self):
            self.updateSelf()
            for i in self.objects:
                i.update()

        def onclick(self,tilePos,pos): 
            '''this will be called when the player clicks'''
            if self.collisionCheck(pos):
                relativePos = [pos[i] - self.position[i] for i in range(2)]
                for i in self.objects:
                    i.onclick(tilePos,relativePos)
                self.selfClick(pos)

        def propertyInit(self):#overwrite this, no exceptions, I dont really want to use abc on UI
            self.BGcolour = self.properties.get("BGcolour",None)
            self.BGimage = self.properties.get("BGimage",None)
            self.minSize = self.properties.get("minSize",[0,0])

        def getSize(self):  
            self.size = self.minSize
            for i in self.objects:
                i.getSize()
            self.selfGetSize()
            for i in range(2):
                if self.size[i] < self.minSize[i]:
                    self.size[i] = self.minSize[i]

        def selfGetSize(self): #overwrite this for elements with multiple elements
            for i in self.objects: # i really didn't want to use an if here
                self.size = i.size

        def getChildrenPos(self) -> list[list]: #overwrite this for elements with multi-element positioning
            return [[0,0]]
            
        def selfClick(self,pos): #overwrite this for interactive elements
            '''this will be called when the player clicks on the element'''

        def updateSelf(self): #overwrite this for non-static elements
            pass

        def redraw(self): #here so i can put it into drawGroup
            pass

    class Container(Base):
        def __init__(self,position = [0,0],parents=[], properties = "default.json",groups = (),zIndex = 0):
            super().__init__(position,parents,properties,groups,zIndex)
            directionIndexDict = {"horizontal":0,"vertical":1}
            self.directionIndex = directionIndexDict[self.direction]
            self.otherDirectionIndex = int(not self.directionIndex)

        def propertyInit(self):
            super().propertyInit()
            self.direction = self.properties.get("direction","horizontal")
            self.spacing = self.properties.get("spacing",0)

        def selfGetSize(self):
            self.size = [0,0]
            for i in self.objects:
                i.getSize()
                self.size[self.directionIndex] += i.size[self.directionIndex] + self.spacing
                if self.size[self.otherDirectionIndex] < i.size[self.otherDirectionIndex]:
                    self.size[self.otherDirectionIndex] = i.size[self.otherDirectionIndex]
            self.size[self.directionIndex] -= self.spacing

        def getChildrenPos(self) -> list[list]:
            positions = [[0,0]]
            for i in range(1,len(self.objects)):
                positions.append(positions[-1].copy())
                positions[-1][self.directionIndex] += self.objects[i-1].size[self.directionIndex] + self.spacing
            return positions

    class Button(Base):
        def __init__(self,funcOnClick, position = [0,0],parents=[], properties = "default.json",groups = (),zIndex = 0):
            super().__init__(position,parents,properties,groups,zIndex)
            self.funcOnClick = funcOnClick

        def propertyInit(self):#placeholder
             super().propertyInit()

        def selfClick(self,pos):
            self.funcOnClick(self)

class Game:
    def __init__(self):
        #window
        info = pygame.display.Info()
        self.gameWindow = pygame.display.set_mode((info.current_w,info.current_h))
        pygame.display.set_caption("Game Window")

        #groups
        self.drawGroup =   GroupCustom() #for objects with draw() method
        self.clickGroup =  GroupCustom() #for objects with onclick() method
        self.updateGroup = GroupCustom() #for objects that have logic that is executed every frame
        self.gridGroup =   GroupCustom() #for objects on grid

        #objects
        self.gameGrid = Grid(self.gameWindow,64,(self.updateGroup,),20)
        self.gameBG =   Background(self.gameGrid,"assets/tile.png",(self.drawGroup,),-10)
        self.playerCam = Camera(self.gameGrid,(0,0),(self.updateGroup,),10)
        self.player =   Player("assets/player.png",self.gameGrid,(0,0),(self.drawGroup,self.clickGroup,self.gridGroup),5)

        #UI
        self.UIscreen = UISimple.Container(groups=(self.drawGroup,self.clickGroup),zIndex=232)
        self.buttontainer = UISimple.Container(parents=[self.UIscreen],properties="PropertiesUI/container.json" )
        self.button = UISimple.Button(funcOnClick=print, parents=[self.buttontainer], properties="PropertiesUI/button.json")
        self.button2 = UISimple.Button(funcOnClick=print, parents=[self.buttontainer], properties="PropertiesUI/button.json")

        self.UIscreen.getSize()

        #variables
        self.pygameClock = pygame.time.Clock()
        self.GAMEFPS = 60
        self.gameCycleEnd = False
        self.frames = 0

    def inputs(self):
        mousepos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.gameCycleEnd = True

                case pygame.MOUSEBUTTONDOWN:
                    print(self.gameGrid.getTileFromPos(mousepos)) #debug
                    for i in self.clickGroup:
                        i.onclick(self.gameGrid.getTileFromPos(mousepos),mousepos)

                case pygame.KEYDOWN:

                    match event.key:

                        case pygame.K_v:
                            self.gameGrid.tileSize += 64
                            print(f"tileSize increased to {self.gameGrid.tileSize}")

                        case pygame.K_b:
                            if self.gameGrid.tileSize - 64 > 0:
                                self.gameGrid.tileSize -= 64
                                print(f"tileSize decreased to {self.gameGrid.tileSize}")
                    
                        case pygame.K_g:
                            for i in self.drawGroup:
                                i.redraw()
                            print(f"grid redraw triggered")

    def gameLoop(self):
        while not self.gameCycleEnd:

            self.inputs()
            self.gameGrid.update()
            self.gameWindow.fill((255,255,255))
            for i in self.updateGroup:
                i.update()
            for i in self.drawGroup:
                i.draw(self.gameWindow)
            self.frames += 1

            pygame.display.flip() 

            self.pygameClock.tick(self.GAMEFPS) 

        pygame.quit()

game = Game()
game.gameLoop()