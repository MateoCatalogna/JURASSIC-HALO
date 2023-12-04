import pygame
from config import *



class Item(pygame.sprite.Sprite):
    def __init__(self, item_type,x, y, player):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.player = player
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        

