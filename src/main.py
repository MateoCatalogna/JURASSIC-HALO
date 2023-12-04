import pygame
from player import Player
from config import *
from level import Level	
from overworld import Overworld


pygame.init()





class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Shooter')
        self.clock = pygame.time.Clock()
        self.run = True  # The game loop will always start
        self.game_started = False  # Added variable to track whether the game has started
        self.shoot = False
        self.moving_left = False
        self.moving_right = False
        self.level_number = 0
        self.player = Player('player', 300, 600, 1, 5, 5, 0)
        self.level = Level(LEVELS[self.level_number], self.screen, self.player, self.create_overworld, self.level_number)
        # self.background_image = pygame.image.load("path/to/background_image.jpg")
        self.timer = LEVEL_TIME
        self.max_level = 0
        self.create_level = self.create_level # Ensure this method is defined
        self.overworld = Overworld(0,self.max_level,self.screen,self.create_level)
        self.status = 'menu'
        self.background_ = pygame.image.load(f"./src/img/Background/{self.level_number}.png")
        self.background = pygame.transform.scale(self.background_,(SCREEN_WIDTH, SCREEN_HEIGHT))




    def create_level(self, level_number):
        self.status = 'world'
        self.level = Level(LEVELS[level_number], self.screen, self.player, self.create_overworld, level_number)





    def create_overworld(self, current_level, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level, self.max_level, self.screen, self.create_level)

        # Check if the player picked up the diamond in the current level
        if self.level.diamond_picked_up():
            # Update the overworld to create a path to the next level
            self.overworld.update_path(current_level, current_level + 1)

        self.status = 'overworld'




    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.moving_left = True
                if event.key == pygame.K_d:
                    self.moving_right = True
                if event.key == pygame.K_w and self.player.alive:
                    self.player.jump = True
                if event.key == pygame.K_SPACE:  # Change to pygame.K_SPACE for shooting
                    self.shoot = True
                if event.key == pygame.K_p:
                    self.pantalla_pausa(screen, font2, button_Resume, button_subir, button_bajar, button_mute, button_unmute)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.moving_left = False
                if event.key == pygame.K_d:
                    self.moving_right = False
                if event.key == pygame.K_SPACE:  # Change to pygame.K_SPACE for shooting
                    self.shoot = False


    def update(self):
        self.player.update_animation()

        if self.player.alive:
            if self.shoot:
                self.player.shoot()
            self.player.lasers.update()
            if self.player.in_air:
                self.player.update_action(2) # 2: jump
            elif self.moving_left or self.moving_right:
                self.player.update_action(1) # 1: run
            else:
                self.player.update_action(0) # 0: idle
            self.player.update(self.moving_left, self.moving_right, self.level.obstacle_list, self.level.moving_plataforms)

            # Check if a diamond has been picked up
            if self.level.diamond_picked_up():
                remaining_time = max(0, LEVEL_TIME - self.timer)  # Calculate remaining time, ensuring it's not negative
                score_increase = remaining_time * 100
                self.player._score += score_increase
                self.level_number += 1
                self.status = 'overworld'
                self.timer = LEVEL_TIME
                self.overworld.max_level = self.level_number

            self.timer -= 1
            if self.timer <= 0:
                self.level.show_game_over_screen()

            self.level.update()
                    

    def handle_level_select(self):
        keys = pygame.key.get_pressed()
        for i in range(len(LEVELS)):
            if keys[pygame.K_1 + i] and 0 <= i < len(LEVELS):
                self.level_number = i
                self.overworld.current_level = i
                self.create_level(self.level_number)
                self.status = 'world'



    def draw(self):
        if self.status == 'menu':
            draw_text(f"JURASSIC HALO", font2, (100,150,20), SCREEN_WIDTH // 2 - 150, 200)
            if start_btn.draw(self.screen):
                self.status = 'overworld'
            if options_btn.draw(self.screen):
                self.pantalla_pausa(screen, font2, button_Resume, button_subir, button_bajar, button_mute, button_unmute)
            if quit_btn.draw(self.screen):
                self.run = False
        elif self.status == 'overworld':
            # Draw level selection screen
            self.screen.fill((0, 0, 0))
            draw_text("Select Level:", font2, WHITE, SCREEN_WIDTH // 2 -100 , SCREEN_HEIGHT // 4 - 100)
            self.overworld.icon.draw(self.screen)
            self.overworld.run()
            pygame.display.flip()
            


        else:

            self.screen.blit(self.background, (0,0))
            self.level.draw()
            self.player.lasers.draw(self.screen)  # Draw lasers on top
            draw_text(f'Ammo:{self.player.ammo}', font, WHITE, 10,35)
            draw_text(f'Lives:{self.player.lives}', font, WHITE, 10,55)
            draw_text(f'Score:{self.player._score}', font, WHITE, 10,15)
            draw_text(f'Time: {max(self.timer // FPS, 0)}s', font, WHITE, SCREEN_WIDTH // 2, 15)
            if self.player.lives == 0:
                draw_text(f'GAME OVER', font2, (160, 0, 50), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                if restart_btn.draw(self.screen):
                    self.reset_game()


        pygame.display.flip()
    

    def handle_level_select(self):
        keys = pygame.key.get_pressed()
        for i in range(len(LEVELS)):
            if keys[pygame.K_1 + i] and 0 <= i < len(LEVELS):
                self.overworld.current_level = i
                self.create_level(i)
                self.status = 'world'



    def reset_game(self):
        self.player.lasers.empty()
        self.level.projectiles_group.empty()
        self.level.enemies.empty()
        self.level.items.empty()
        self.level.plataforms.empty()
        self.level.traps.empty()
        self.level.bosses.empty()

        # Reset player attributes like ammo, lives, and score
        self.player.reset()

        # Reset player's position and state
        self.player.rect.x = 0  # Reset player's x position to 0
        self.player.rect.y = 0  # Reset player's y position to 0
        self.player.alive = True  # Reset player's alive state to True

        # Reinitialize level with the same level data
        self.level = Level(LEVELS[self.level_number], self.screen, self.player, self.create_overworld, self.level_number)
        self.level.gameover = False
        self.game_started = True


    def pantalla_pausa(self, screen, fuente, button_resume, button_vol_up, button_vol_down, button_mute, button_unmute): 

        
        screen.fill(black)
        draw_text("PAUSE", fuente, (100,150,20), SCREEN_WIDTH // 2 - 25, 50)

        pygame.display.flip()
        paused = True

        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if paused:
                if button_resume.draw(screen):
                    paused = False

                # Verificar clic en otros botones y realizar acciones correspondientes
                if button_vol_up.draw(screen):
                    # Aumentar volumen
                    pygame.mixer.music.set_volume(min(1.0, pygame.mixer.music.get_volume() + 0.1))
                elif button_vol_down.draw(screen):
                    # Disminuir volumen
                    pygame.mixer.music.set_volume(max(0.0, pygame.mixer.music.get_volume() - 0.1))
                elif button_mute.draw(screen):
                    # Silenciar
                    pygame.mixer.music.set_volume(0.0)
                elif button_unmute.draw(screen):
                    # Quitar el silencio
                    pygame.mixer.music.set_volume(1.0)

                # Verificar si el juego se reanudó
                if not paused:
                    pygame.mixer.music.unpause()

                pygame.display.flip()



    def run_game(self):
        pygame.mixer.music.load("./src/snd/music.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.1)
        while self.run:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        self.close()

    def close(self):
        pygame.quit()


game = Game()
game.run_game()
