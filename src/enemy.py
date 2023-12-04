import pygame
import os
from config import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, player):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self.speed = speed
        self.direction = 1
        self.flipped = False
        self.width = 50
        self.height = 50
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.hit = False
        self.hit_time = 0
        self.lives = 1

        animation_types = ['Run', 'Dead']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'./src/img/enemy/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'./src/img/enemy/{animation}/{i}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, obstacle_list, moving_platforms):
        dx = self.speed * self.direction
        collided = False

        if self.rect.right + dx > SCREEN_WIDTH or self.rect.left + dx < 0:
            self.direction *= -1
            self.flipped = not self.flipped
            collided = True

        for obstacle in obstacle_list + moving_platforms:
            if self.rect.colliderect(obstacle.rect):
                if not collided:
                    self.direction *= -1
                    self.flipped = not self.flipped
                    collided = True
                break

        if not collided:
            self.rect.x += dx
        else:
            # Ajustar la posición después de una colisión
            self.rect.x -= dx

        self.update_animation()
    

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]

        if self.flipped:
            self.image = pygame.transform.flip(self.image, True, False)

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0


    def collide_with_laser(self):
        self.lives -= 1
        enemy_sound.play()
        self.player._score += 5
        if self.lives <= 0:
            self.kill()

    def draw(self, screen):
        if self.lives == 1:
            screen.blit(self.image, self.rect)


