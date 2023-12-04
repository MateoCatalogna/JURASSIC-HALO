import pygame
from config import *

class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, platforms):
        pygame.sprite.Sprite.__init__(self)
        self.plataforms = platforms
        self.speed = 10
        self.image = pygame.image.load("./src/img/utilities/fireball.png").convert_alpha() 
        self.image = pygame.transform.scale(self.image, (60,60))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction


    def update(self):
        self.rect.x += (self.direction * self.speed)
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
