import pygame
import os
import math

pygame.init()

#classes
class grid():
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
    def __init__(self,grid: grid,image = None):
        self.image = image
        self.grid = grid
        self.drawBG()

    def drawBG(self):
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

    def updateBG(self):
        startPosition = self.grid.getPosFromTile((-1,-1))
        trueOffset = [i - math.floor(i/self.tileSize) * self.tileSize for i in self.grid.offset]
        position = [startPosition[index] - trueOffset[index] for index in range(len(startPosition))]
        self.grid.surface.blit(self.background,position)

class SpritesBase(pygame.sprite.Sprite):
    def __init__(self,image,x,y,width,height,groups = ()):
        super().__init__(*groups)
        self.original_image = image
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),self.original_image)),(width,height))
        self.rect = self.image.get_rect(topleft = (x,y))

    def draw(self,window, pos = None):
        if pos == None:
            window.blit(self.image,self.rect)
        else:
            window.blit(self.image,pos)


class Sprites(SpritesBase):
    def __init__(self,image,grid: grid,tilePos:tuple,groups: tuple = ()):
        pos = grid.getPosFromTile(tilePos)
        size = (grid.tileSize,grid.tileSize)
        self.grid = grid 
        super().__init__(image,pos[0],pos[1],size[0],size[1],groups)
    
    def draw(self,window, pos=None): # pos=None is just here to remove the error
        originalPosition = [self.rect.left,self.rect.top] # type: ignore , Im too lazy to fix this
        position =[originalPosition[index]-self.grid.offset[index] for index in range(len(originalPosition))]
        super().draw(window,position)


spritesGroup = pygame.sprite.Group()
info = pygame.display.Info()
game_window = pygame.display.set_mode((info.current_w,info.current_h), pygame.RESIZABLE)

pygame.display.set_caption("Game Window")

#objects
gameGrid=grid(game_window,48)
player = Sprites("assets/player.png",gameGrid,(4,4),(spritesGroup,))
gameBG = Background(gameGrid)

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

    if not game_pause:
        gameGrid.update()
        game_window.fill((255,255,255))
        gameBG.updateBG()
        for i in spritesGroup:
            i.draw(game_window)
        frames += 1


    pygame.display.flip() 

    Pygame_Clock.tick(Game_FPS) 

pygame.quit()