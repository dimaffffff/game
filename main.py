import pygame
import os
import math
import copy
import abc
pygame.init()

class General:
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

class GroupCustom:
    def __init__(self):
        self.objects=[]
        self.zIndexes = {}

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
            General.addToGroups(self,groups,zIndex)
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
        General.addToGroups(self,groups,zIndex)
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
            tile = SpritesBase.loadImage(self.image,(self.tileSize,self.tileSize))

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
        General.addToGroups(self,groups,zIndex)
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
        General.addToGroups(self,groups,zIndex)
        self.load(image,(width,height),(x,y))
        self.originalImage = image

    @staticmethod
    def loadImage(filePath,size:tuple):
        return pygame.transform.scale(
            pygame.image.load(
                os.path.join(os.path.dirname(os.path.abspath(__file__)),filePath)
                ),
            size
        )

    def load(self,filename,size:tuple,pos:tuple):
        self.image = self.loadImage(filename,size)
        
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

class Game:
    def __init__(self):
        #window
        info = pygame.display.Info()
        self.gameWindow = pygame.display.set_mode((info.current_w,info.current_h))
        pygame.display.set_caption("Game Window")

        #groups
        self.drawGroup =        GroupCustom() #for objects with draw() method
        self.gridGroup =        GroupCustom() #for objects on the gameGrid
        self.updateGroup =      GroupCustom() #for objects that have logic that is executed every frame

        #objects
        self.gameGrid = Grid(self.gameWindow,64,(self.updateGroup,),20)
        self.gameBG =   Background(self.gameGrid,"assets/tile.png",(self.drawGroup,),-10)
        self.playerCam = Camera(self.gameGrid,(0,0),(self.updateGroup,),10)
        self.player =   Player("assets/player.png",self.gameGrid,(0,0),(self.drawGroup,self.gridGroup),5)
        

        #variables
        self.pygameClock = pygame.time.Clock()
        self.GameFPS = 60
        self.gameCycleEnd = False
        self.frames = 0

    def gameLoop(self):
        while not self.gameCycleEnd:
            mousepos = pygame.mouse.get_pos()
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.gameCycleEnd = True

                if event.type == pygame.MOUSEBUTTONDOWN:
                    print(self.gameGrid.getTileFromPos(mousepos))

                    for i in self.gridGroup:
                        i.onclick(self.gameGrid.getTileFromPos(mousepos),mousepos)
                    print(General.getObjectOnTile(self.gridGroup,self.gameGrid.getTileFromPos(mousepos)))

                if event.type == pygame.KEYDOWN and event.key == pygame.K_v:
                    self.gameGrid.tileSize += 64
                    print(f"tileSize increased to {self.gameGrid.tileSize}")

                if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                    if self.gameGrid.tileSize - 64 > 0:
                        self.gameGrid.tileSize -= 64
                        print(f"tileSize decreased to {self.gameGrid.tileSize}")
                        
                if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                    for i in self.drawGroup:
                        i.redraw()
                    print(f"grid redraw triggered")

            self.gameGrid.update()
            self.gameWindow.fill((255,255,255))
            for i in self.updateGroup:
                i.update()
            for i in self.drawGroup:
                i.draw(self.gameWindow)
            self.frames += 1



            pygame.display.flip() 

            self.pygameClock.tick(self.GameFPS) 

        pygame.quit()

game = Game()
game.gameLoop()