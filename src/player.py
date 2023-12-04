import pygame
import os
from laser import Laser
from config import *



class Player(pygame.sprite.Sprite):
    def __init__(self, player, x, y, scale, speed, ammo, score):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.player = player
        self.speed = speed
        self._ammo = ammo  # Use a different name for the private variable
        self.start_ammo = ammo
        self._score = score  # Use a different name for the private variable
        self.start_score = score
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.lasers = pygame.sprite.Group()
        self.lives = 3
        self._high_score = 0
        self.load_high_score()



        animation_types = ['Idle', 'Run', 'Jump']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count the number of files in the folder
            num_of_frames = len(os.listdir(f'./src/img/{self.player}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'./src/img/{self.player}/{animation}/{i}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    @property
    def lives(self):
        return self._lives

    @lives.setter
    def lives(self, value):
        if value <= 0:
            self._lives = 0
            self.alive = False
            
        else:
            self._lives = value


    @property
    def ammo(self):
        return self._ammo

    @ammo.setter
    def ammo(self, value):
        self._ammo = value if value >= 0 else 0


    @property
    def high_score(self):
        return self._high_score

    @high_score.setter
    def high_score(self, value):
        self._high_score = value if value >= 0 else 0
        self.save_high_score()

    def load_high_score(self):
        try:
            with open('high_score.json', 'r') as file:
                data = json.load(file)
                self._high_score = data.get('high_score', 0)
        except FileNotFoundError:
            # If the file is not found, set high score to 0
            self._high_score = 0

    def save_high_score(self):
        data = {'high_score': self._high_score}
        with open('high_score.json', 'w') as file:
            json.dump(data, file)


    def increase_score(self, amount):
        # Update the score and check if it's a new high score
        super().increase_score(amount)
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()



    def reset(self):
        self.ammo = self.start_ammo
        self.lives = 3  # O cualquier valor predeterminado que desees
        self._score = self.start_score

    def update(self, moving_left, moving_right, obstacle_list, moving_platforms):
        dx = 0
        dy = 0

        # Asigna variables de movimiento si se mueve a la izquierda o derecha
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Salto
        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # Aplica gravedad
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Comprueba la colisión con el suelo y obstáculos
        for tile in obstacle_list:
        # Check colisión en la dirección x
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
            # Check colisión en la dirección y
            if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                # Comprueba si está debajo del suelo, es decir, saltando
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile.rect.bottom - self.rect.top
                # Comprueba si está por encima del suelo, es decir, cayendo
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile.rect.top - self.rect.bottom

    # Comprueba la colisión con las plataformas en movimiento
            for platform in moving_platforms:
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                    dx = platform.move_x  # Ajusta la posición en x según la velocidad de la plataforma

                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                    if self.vel_y < 0:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    elif self.vel_y >= 0:
                        self.vel_y = 0
                        self.in_air = False
                        dy = platform.rect.top - self.rect.bottom

        # Actualiza la posición del rectángulo
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy

        # Asegúrate de que el jugador no se salga de los límites de la pantalla
        if 0 <= new_x <= SCREEN_WIDTH - self.rect.width:
            self.rect.x = new_x
        if 0 <= new_y <= 650:  # Ajusta según tus necesidades
            self.rect.y = new_y

        self.update_animation()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


    def collide_with_boss(self):
        # This method is called when the player collides with the boss
        self.lives -= 1  # Subtract one life

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:  # Sin paréntesis aquí
            laser_sound.play()
            self.shoot_cooldown = 20
            laser = Laser(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery - 27, self.direction)
            self.lasers.add(laser)
            # Reduce ammo
            self.ammo -= 1

    def reset(self):
        self.ammo = self.start_ammo
        self.lives = 3

    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

