import pygame
from config import TILE_SIZE

class Tile(pygame.sprite.Sprite):
    def __init__(self, position, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect(topleft=position)



    def draw(self, screen):
         screen.blit(self.image, self.rect)


    