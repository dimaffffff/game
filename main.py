import pygame
import os
import math

pygame.init()

#classes
class TileSet():
        def __init__(self, surface: pygame.Surface,tileSize:int):       
            self.surface = surface
            self.surfaceSize = self.surface.get_size()
            self.tileSize = tileSize

        def getPosFromTile(self,tile: tuple):
            return tuple([axis * self.tileSize for axis in tile])
        
        def getTileFromPos(self,pos:tuple):
            tile = [axis / self.tileSize for axis in pos]
            tile = [math.floor(i) for i in tile]
            return tile
        

class SpritesBase(pygame.sprite.Sprite):
    def __init__(self,image,x,y,width,height,groups = ()):
        super().__init__(*groups)
        self.original_image = image
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),self.original_image)),(width,height))
        self.rect = self.image.get_rect(topleft = (x,y))

    def draw(self, window):
        window.blit(self.image,self.rect)


class Sprites(SpritesBase):
    def __init__(self,image,tileSet: TileSet,tilePos:tuple,groups: tuple = ()):
        pos = tileSet.getPosFromTile(tilePos)
        size = (tileSet.tileSize,tileSet.tileSize)
        super().__init__(image,pos[0],pos[1],size[0],size[1],groups)


spritesGroup = pygame.sprite.Group()
info = pygame.display.Info()
game_window = pygame.display.set_mode((info.current_w,info.current_h), pygame.RESIZABLE)

pygame.display.set_caption("Game Window")

#objects
gameTileSet=TileSet(game_window,48)
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