import pygame
import os
from config import *
from fireball import Fireball
from item import Item

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, player, projectiles_group, platforms, items):
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
        self.lives = 5  # Adjust the number of lives as needed
        self.projectiles_group = projectiles_group
        self.is_shooting = False  # New variable to track shooting state
        self.shoot_start_time = 0
        self.shoot_duration = 500  # Adjust the duration of the shooting animation as needed
        self.is_attacking = False
        self.last_shoot_time = pygame.time.get_ticks()
        self.shoot_cooldown = 1000
        self.platforms = platforms
        self.has_spawned_star = False
        self.items = items


        animation_types = ['run', 'dead', 'atack']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'./src/img/boss/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'./src/img/boss/{animation}/{i}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, obstacle_list, moving_platforms):
        self.move(obstacle_list + moving_platforms)
        self.shoot()
        self.update_animation()



    def move(self, obstacles):
        dy = self.speed * self.direction
        dx = self.speed * self.direction
        collided = False
        

        if self.rect.right + dy > SCREEN_WIDTH or self.rect.top + dy < 0:
            self.direction *= -1
            self.flipped = not self.flipped
            collided = True

        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if not collided:
                    self.direction *= -1
                    self.flipped = not self.flipped
                    collided = True
                break

        if not collided:
            self.rect.y += dy
        else:
            # Adjust the position after a collision
            self.rect.y -= dy

        if self.lives <= 2:
            if not collided:
                self.rect.x += dx
            else:
                # Adjust the position after a collision
                self.rect.x -= dx

        self.update_animation()


    def shoot(self):
        current_time = pygame.time.get_ticks()
        fireball_sound.play()
        if current_time - self.last_shoot_time > self.shoot_cooldown:
            self.is_shooting = True
            self.is_attacking = True
            self.shoot_start_time = current_time
            self.action = 2
            self.frame_index = 0

            # Determine projectile direction based on boss's direction
            projectile_direction = self.direction 

            new_projectile = Fireball(self.rect.centerx, self.rect.centery, projectile_direction, self.platforms)
            self.projectiles_group.add(new_projectile)
            self.last_shoot_time = current_time


    def animate_shoot(self):
    # Separate method to handle shooting animation
        ANIMATION_COOLDOWN = 100

        if 0 <= self.action < len(self.animation_list):
            current_animation = self.animation_list[self.action]
            if 0 <= self.frame_index < len(current_animation):
                if pygame.time.get_ticks() - self.shoot_start_time > self.shoot_duration:
                    self.is_shooting = False
                    self.is_attacking = False
                    self.action = 0  # Switch back to the run animation
                    self.frame_index = 0
                else:
                    if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                        self.update_time = pygame.time.get_ticks()
                        self.frame_index += 1

                    if self.frame_index >= len(current_animation):
                        self.frame_index = 0

                    if self.direction == 1:
                        # Flip the image when facing left
                        self.image = pygame.transform.flip(current_animation[self.frame_index], True, False)
                    else:
                        self.image = current_animation[self.frame_index]


    def collide_with_laser(self, laser):
        self.lives -= 1
        hurt_sound.play()
        if self.lives <= 0 and not self.has_spawned_star:
            die_boss_sound.play()
            self.action = 1  # Cambia a la animación de muerte
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()  # Reinicia el temporizador de animación
            self.death_start_time = pygame.time.get_ticks()  # Registra el tiempo de inicio de la animación de muerte
            self.kill()
            star = Item("Star", self.rect.x, self.rect.y, self.player)
            self.items.add(star)
            self.has_spawned_star = True



    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        DEATH_DELAY = 500  # Ajusta la duración del retraso antes de desaparecer (en milisegundos)

        if 0 <= self.action < len(self.animation_list):
            current_animation = self.animation_list[self.action]
            if 0 <= self.frame_index < len(current_animation):
                if self.is_attacking:
                    self.animate_shoot()
                else:
                    self.image = current_animation[self.frame_index]

                    if self.action == 1:  # Animación de muerte
                        if pygame.time.get_ticks() - self.death_start_time > ANIMATION_COOLDOWN:
                            if pygame.time.get_ticks() - self.update_time > DEATH_DELAY:
                                self.kill()  # Elimina la instancia del Boss después del retraso
                    else:
                        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                            self.update_time = pygame.time.get_ticks()
                            self.frame_index += 1

                            if self.frame_index >= len(current_animation):
                                self.frame_index = 0

                            if self.flipped and not self.is_attacking:
                                self.image = pygame.transform.flip(self.image, True, False)



    def draw(self, screen):
        if self.lives > 0:
            screen.blit(self.image, self.rect)