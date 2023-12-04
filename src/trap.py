import pygame
from config import TILE_SIZE

class Trap(pygame.sprite.Sprite):
  def __init__(self, position, image):
      pygame.sprite.Sprite.__init__(self)
      self.image = image
      self.image = pygame.transform.scale(self.image, (25, 25))
      self.rect = self.image.get_rect(topleft=position)
      self.activated = False


  def draw(self, screen):
      screen.blit(self.image, self.rect)