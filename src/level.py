from tile import Tile
from config import *
from item import Item
from enemy import Enemy
from player import Player
from movetile import Plataform
from trap import Trap
from boss import Boss
import sys

class Level:
    def __init__(self, layout, screen, player,create_overworld, level_number):
        self.player = player
        self.layout = layout
        self.screen = screen
        self.level_number = level_number
        self.all_sprites = pygame.sprite.Group()
        self.tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.plataforms = pygame.sprite.Group()
        self.traps = pygame.sprite.Group()
        self.bosses = pygame.sprite.Group()
        self.projectiles_group = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        self.obstacle_list = []  # Initialize the obstacle_list here
        self.moving_plataforms = []
        self.setup_level(layout)
        self.boss = Boss(x=100, y=100, scale=2, speed=5, player =self.player, projectiles_group=self.projectiles_group, platforms=self.plataforms,items = self.items)
        self.star_created = False
        self.gameover = False
        self.create_overworld = create_overworld
        level_data = levels[self.level_number]
        self.new_max_level = level_data['unlock']



    def check_win(self):
        if self.diamond_picked_up():
            self.create_overworld(self.level_number,self.new_max_level)

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DELETE]:
            self.create_overworld(self.layout,self.new_max_level)
        if keys[pygame.K_INSERT]:
            self.create_overworld(self.layout, 0)
        


    def setup_level(self, layout):
        for y, row in enumerate(layout):
            for x, cell in enumerate(row):
                if cell == "P":
                    self.player.rect.x = x * TILE_SIZE
                    self.player.rect.y = y * TILE_SIZE

                elif cell == "1":
                    img = cargar_imagen("Tiles", 1)
                    tile = Tile((x * TILE_SIZE, y * TILE_SIZE), img)
                    self.tiles.add(tile)
                    self.obstacle_list.append((tile))

                elif cell == "2":
                    img = cargar_imagen("Tiles", 2)
                    tile = Tile((x * TILE_SIZE, y * TILE_SIZE), img)
                    self.tiles.add(tile)
                    self.obstacle_list.append(tile)

                elif cell == "7" or cell == "8":
                    img = cargar_imagen("Tiles", 2)
                    platform_speed = 2 if cell == "7" else -2
                    plataforma = Plataform(x * TILE_SIZE, y * TILE_SIZE, platform_speed, 0, img)
                    self.plataforms.add(plataforma)
                    self.moving_plataforms.append(plataforma)

                elif cell == "9" or cell == "X":
                    img = cargar_imagen("Tiles", 2)
                    platform_speed = 2 if cell == "9" else -2
                    plataforma = Plataform(x * TILE_SIZE, y * TILE_SIZE, 0, platform_speed, img)
                    self.plataforms.add(plataforma)
                    self.moving_plataforms.append(plataforma)



                elif cell == "5":
                    enemy = Enemy(x * TILE_SIZE, y * TILE_SIZE, 1, 7, self.player)
                    self.enemies.add(enemy)

                elif cell == "3" or cell == "4" or cell == "6" or cell == "D":
                    item_type = ""
                    if cell == "3":
                        item_type = "Ammo"
                    elif cell == "4":
                        item_type = "Health"
                    elif cell == "6":
                        item_type = "Coin"
                    elif cell == "D":
                        item_type = "Diamond"
                    elif self.boss.lives <= 0:
                        item_type = "Star"
                    item = Item(item_type, x * TILE_SIZE, y * TILE_SIZE, self.player)
                    self.items.add(item)
                
                elif cell == "T":
                    img = cargar_imagen("Tiles", 3)
                    trap = Trap((x * TILE_SIZE, y * TILE_SIZE + 30), img)
                    self.traps.add(trap)
                
                elif cell == "B" :
                    boss_position = (x * TILE_SIZE, y * TILE_SIZE)
                    boss_scale = 1.5
                    boss_speed = 5
                    boss = Boss(x * TILE_SIZE, y * TILE_SIZE, boss_scale, boss_speed, self.player, self.projectiles_group, self.plataforms, self.items)
                    self.bosses.add(boss)







    def update(self):
        dx = 0
        dy= 0
        enemies_hit_by_player = pygame.sprite.spritecollide(self.player, self.enemies, False)
        traps_hit_by_player = pygame.sprite.spritecollide(self.player, self.traps, False)
        play_uh_sound = False

        for enemy in enemies_hit_by_player:
            if not enemy.hit:
                self.player.lives -= 1
                enemy.hit = True
                enemy.hit_time = pygame.time.get_ticks()
                play_uh_sound = True
                uh_sound.play()


        for enemy in self.enemies:
            if enemy.hit and pygame.time.get_ticks() - enemy.hit_time > RESET_HIT_TIME:
                enemy.hit = False

        lasers_hit_by_enemy = pygame.sprite.groupcollide(self.player.lasers, self.enemies, True, False)
        for hit_enemies in lasers_hit_by_enemy.values():
            for enemy in hit_enemies:
                enemy.collide_with_laser()
    

        items_hit_by_player = pygame.sprite.spritecollide(self.player, self.items, True)
        for item in items_hit_by_player:
            if item.item_type == "Ammo":
                self.player.ammo += 1
                item_sound.play()
            elif item.item_type == "Health":
                self.player.lives += 1
                item_sound.play()
            elif item.item_type == "Coin":
                self.player._score += 1
                coin_sound.play()
            elif item.item_type == "Star":
                self.show_victory_screen()
            
            item.kill()

        traps_hit_by_player = pygame.sprite.spritecollide(self.player, self.traps, False)
        if traps_hit_by_player and self.player.lives > 0:
            self.player.lives -= 1
            play_uh_sound = True
            uh_sound.play()

            for trap in traps_hit_by_player:
                trap.kill()

        player_hit = pygame.sprite.spritecollide(self.player, self.projectiles_group, True)
        for hit in player_hit:
            self.player.lives -= 1
        

        lasers_hit_by_boss = pygame.sprite.groupcollide(self.player.lasers, self.bosses, True, False)
        for hit_bosses in lasers_hit_by_boss.values():
            for boss in hit_bosses:
                boss.collide_with_laser(self.player.lasers)

        star_collected = pygame.sprite.spritecollide(self.player, self.items, False, pygame.sprite.collide_rect)

        if star_collected and not self.star_created:
            self.show_victory_screen()
            self.star_created = True


        self.enemies.update(self.obstacle_list, self.moving_plataforms)
        self.items.update()
        self.plataforms.update()
        self.bosses.update(self.obstacle_list, self.moving_plataforms)
        self.projectiles_group.update()

    def diamond_picked_up(self):
        diamonds_hit_by_player = pygame.sprite.spritecollide(self.player, self.items, False)
        for diamond in diamonds_hit_by_player:
            if diamond.item_type == "Diamond":
                self.player.reset()
                return True
        return False

    def show_victory_screen(self):
        win.play()
        self.screen.fill((0, 0, 0))

        # Show the victory text
        draw_text("YOU WIN!", font, (255, 255, 255), SCREEN_WIDTH // 2 , SCREEN_HEIGHT // 2 - 50)

        # Show the score (assuming you have a score variable)
        draw_text(f"SCORE: {self.player._score}", font, (255, 255, 255), SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 50)

        draw_text(f"HIGH SCORE: {self.player.high_score}", font, (255, 255, 255), SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 120)
        self.check_win()
        pygame.display.flip()  # Update the screen
        pygame.time.delay(5000)  # Wait for a few seconds before exiting (adjust as needed)
        pygame.quit()

    def show_game_over_screen(self):
        gameover.play()
        while not self.gameover:
            # Clear the screen
            self.screen.fill((0, 0, 0))

            # Display game over text
            draw_text("¡Game Over!", font2, (255, 255, 255), SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50)

            # Display score
            draw_text(f"SCORE: {self.player._score}", font2, (255, 255, 255), SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50)
            draw_text(f"HIGH SCORE: {self.player.high_score}", font, (255, 255, 255), SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 120)


            for event in pygame.event.get():  # Handle events
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                    elif event.key == pygame.K_r:
                        self.reset_level()
                        self.gameover = False
            pygame.display.flip()




    def draw(self):
        self.input()
        self.tiles.draw(self.screen)
        self.enemies.draw(self.screen)
        self.items.draw(self.screen)
        self.player.draw(self.screen)   
        self.plataforms.draw(self.screen)
        self.traps.draw(self.screen)
        self.bosses.draw(self.screen)
        self.projectiles_group.draw(self.screen)

        
