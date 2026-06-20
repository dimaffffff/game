import pygame
import os
import random

pygame.init()

#classes
class Array3D:
    def __init__(self,width,height):
        self.array = []
        for y in range(int(height)):
            self.array.append([])
            for x in range(int(width)):
                self.array[y].append([])
        self.width = width
        self.height = height

    def getItems(self,pos:tuple):
        return self.array[pos[1]][pos[0]]
    
    def addItem(self,pos:tuple,item):
        self.array[pos[1]][pos[0]].append(item)

    def setItems(self,pos:tuple,value):
        self.array[pos[1]][pos[0]] = value

    def __str__(self):
        return str(self.array)
    
class TileSet(Array3D):
        def __init__(self, surface: pygame.Surface,size:tuple):       
            self.surface = surface
            self.surfaceSize = self.surface.get_size()
            self.tileAmountX = size[0]
            self.tileAmountY = size[1]
            self.tileSpacingX = int(self.surfaceSize[0] / self.tileAmountX)
            self.tileSpacingY = int(self.surfaceSize[1] / self.tileAmountY)
            super().__init__(self.tileAmountX,self.tileAmountY)

        def getPos(self,tile: tuple):
            return (tile[0]*self.tileSpacingX, tile[1]*self.tileSpacingY)
        
class SpritesBase(pygame.sprite.Sprite):
    def __init__(self,image,x,y,width,height,groups = []):
        super().__init__(*groups)
        self.original_image = image
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),self.original_image)),(width,height))
        self.rect = self.image.get_rect(topleft = (x,y))

    def draw(self, window):
        window.blit(self.image,self.rect)


class Sprites(SpritesBase):
    def __init__(self,image,tileSet: TileSet,tilePos:tuple,groups = ()):
        pos = (tilePos[0] * tileSet.tileSpacingX, tilePos[1] * tileSet.tileSpacingY)
        size = (tileSet.tileSpacingX,tileSet.tileSpacingY)
        tileSet.addItem(tilePos,self)
        super().__init__(image,pos[0],pos[1],size[0],size[1],groups)


spritesGroup = pygame.sprite.Group()

game_window = pygame.display.set_mode((800,800))

pygame.display.set_caption("Game Window")

#objects
gameTileSet=TileSet(game_window,(10,10))
player = Sprites("assets/player.png",gameTileSet,(4,4),(spritesGroup,))

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


    if not game_pause:
        game_window.fill((255,255,255))
        for i in spritesGroup:
            i.draw(game_window)
        frames += 1


    pygame.display.flip() 

    Pygame_Clock.tick(Game_FPS) 

pygame.quit()