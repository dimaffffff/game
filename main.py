import pygame
import os
import math
import copy

pygame.init()

#classes

class GroupCustom:
    def __init__(self):
        self.dict = {
            "object": [],
            "z-index": []
        }

    def sortByzIndex(self):#this code is not good in any way, shape, or form
        end = False
        while not end:
            end = True
            for i in range(len(self.dict["z-index"])):
                if i + 1 != len(self.dict["z-index"]):
                    if self.dict["z-index"][i] > self.dict["z-index"][i+1]:
                        end = False
                        swapNum = (self.dict["object"][i],self.dict["z-index"][i])
                        self.dict["object"][i] = self.dict["object"][i+1]
                        self.dict["object"][i+1] = swapNum[0]
                        self.dict["z-index"][i] = self.dict["z-index"][i+1]
                        self.dict["z-index"][i+1] = swapNum[1]

    def add(self,object,zIndex = 0):
        self.dict["object"].append(object)
        self.dict["z-index"].append(zIndex)
        self.sortByzIndex()
        
    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.dict["object"]):
            returnValue = self.dict["object"][self.index]
            self.index += 1
            return returnValue
        else:
            raise StopIteration

class Grid:
        def __init__(self, surface: pygame.Surface,tileSize:int):       
            self.surface = surface
            self.surfaceSize = self.surface.get_size()
            self.tileSize = tileSize
            self.offset = [0,0]


        def getPosFromTile(self,tile: tuple):
            return tuple([axis * self.tileSize for axis in tile])
        
        def getTileFromPos(self,pos:tuple):
            pos = [pos[index]+self.offset[index] for index in range(len(pos))] #type: ignore
            tile = [axis / self.tileSize for axis in pos]
            tile = [math.floor(i) for i in tile]
            return tile
            
        
        def update(self):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.offset[0] -= 10
            if keys[pygame.K_d]:
                self.offset[0] += 10
            if keys[pygame.K_w]:
                self.offset[1] -= 10
            if keys[pygame.K_s]:
                self.offset[1] += 10

class Background:  #TODO: support for images
    def __init__(self,grid: Grid,image = None,groups = (),zIndex = 0):
        self.image = image
        for group in groups:
            group.add(self,zIndex)
        self.updateBG(grid)

    def updateBG(self,grid: Grid):
        self.grid = copy.copy(grid)
        self.tileSize = self.grid.tileSize
        self.surfaceSize = self.grid.surfaceSize

        self.background = pygame.Surface([self.tileSize*2+i for i in self.surfaceSize])

        tilesOnSurface = [math.ceil(axisSize/self.tileSize) for axisSize in self.background.get_size()]

        tile = pygame.Surface((self.tileSize,self.tileSize))
        tile.fill((255,255,255))
        if self.image == None: 
            pygame.draw.rect(tile,"red",pygame.Rect((0,0),(self.tileSize,self.tileSize)),int(self.tileSize/32))

        for x in range(tilesOnSurface[0]):
            for y in range(tilesOnSurface[1]):
                self.background.blit(tile,self.grid.getPosFromTile((x,y))) 

    def draw(self,window):
        startPosition = self.grid.getPosFromTile((-1,-1))
        trueOffset = [i - math.floor(i/self.tileSize) * self.tileSize for i in self.grid.offset]
        position = [startPosition[index] - trueOffset[index] for index in range(len(startPosition))]
        window.blit(self.background,position)

class SpritesBase(pygame.sprite.Sprite):
    def __init__(self,image,x,y,width,height,groups = (),zIndex = 0):
        super().__init__()
        for group in groups:
            group.add(self,zIndex)
        self.original_image = image
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),self.original_image)),(width,height))
        self.rect = self.image.get_rect(topleft = (x,y))

    def draw(self,window, pos = None):
        if pos == None:
            window.blit(self.image,self.rect)
        else:
            window.blit(self.image,pos)

class Sprites(SpritesBase):
    def __init__(self,image,grid: Grid,tilePos:tuple,groups: tuple = (),zIndex = 0):
        pos = grid.getPosFromTile(tilePos)
        size = (grid.tileSize,grid.tileSize)
        self.grid = grid 
        super().__init__(image,pos[0],pos[1],size[0],size[1],groups,zIndex)
    
    def draw(self,window, pos=None): # pos=None is just here to remove the error
        originalPosition = [self.rect.left,self.rect.top] # type: ignore , Im too lazy to fix this
        position =[originalPosition[index]-self.grid.offset[index] for index in range(len(originalPosition))]
        super().draw(window,position)


spritesGroup = GroupCustom()
info = pygame.display.Info()
game_window = pygame.display.set_mode((info.current_w,info.current_h), pygame.RESIZABLE)

pygame.display.set_caption("Game Window")

#objects
gameGrid=Grid(game_window,48)
gameBG = Background(gameGrid,None,(spritesGroup,),-10)
player = Sprites("assets/player.png",gameGrid,(4,4),(spritesGroup,),5)



#variables
Pygame_Clock = pygame.time.Clock()
Game_FPS = 60
game_cycle_end = False
game_pause = False
frames = 0

while not game_cycle_end:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_cycle_end = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(gameGrid.getTileFromPos(pygame.mouse.get_pos()))
        if event.type == pygame.KEYDOWN and event.key == pygame.K_v:
            gameGrid.tileSize += 64
            print(f"tileSize increased to {gameGrid.tileSize}")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            gameGrid.tileSize -= 64
            print(f"tileSize decreased to {gameGrid.tileSize}")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
            gameBG.updateBG(gameGrid)
            print(f"grid redraw triggered")

    if not game_pause:
        gameGrid.update()
        game_window.fill((255,255,255))
        for i in spritesGroup:
            i.draw(game_window)
        frames += 1


    pygame.display.flip() 

    Pygame_Clock.tick(Game_FPS) 

pygame.quit()