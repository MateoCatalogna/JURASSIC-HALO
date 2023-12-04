import pygame
import os
import json
from button import Button
import sys

pygame.init()

FPS = 60
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 650

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Your Game Title')

LEVELS = [
    [
        "100000000000000000000000",
        "100000000000000000000000",
        "1D00000000000000000000000",
        "122006500000000000000000",
        "100000800000060000006000",
        "100000000000700000000000",
        "100000000000000661000000",
        "10000000000000T211105400",
        "100000000000032111000110",
        "100000000000621111000000",
        "1P0000000006211111000000",
        "100003T00T62111111TTTTTT",
        "122222222221111111222222"
    ],
    [
        "100000000000000000000000",
        "1D0000050000000000000000",
        "122000006000006000000000",
        "100000800007000020020000",
        "100000000000000000000060",
        "100000000000000005000000",
        "100000000000000000030090",
        "100000000006000000020000",
        "100050004002000800000000",
        "100060007000000000000000",
        "100620000000000000000000",
        "1P021TTTTTTTTTTTTTTTTTTT",
        "122212222222222222222222"
    ],
    [
        "100000000000000000000001",
        "100008000000000000000001",
        "100000000000000000100001",
        "100000000000000000000001",
        "100000000000000000106001",
        "1000X00000000000000X001",
        "100000000000000000100001",
        "1000000000000000B0000301",
        "140900000000000000100091",
        "126000000000000000000001",
        "11260P003003000040000001",
        "111221111122222222222222",
        "111111111111111111111111"
    ]
]

with open('levels.json', 'w') as json_file:
    json.dump({'levels': LEVELS}, json_file)


level_0 = {'node_pos':(300,400), 'content': 'level 0', 'unlock': 1}
level_1 = {'node_pos':(600,220), 'content': 'level 1', 'unlock': 2}
level_2 = {'node_pos':(880,500), 'content': 'level 2', 'unlock': 3}


levels = {
    0: level_0,
    1: level_1,
    2: level_2

}

TILE_SIZE = 50

def cargar_imagen(type, index):
    img_path = f'./src/img/{type}/{index}.png'
    img = pygame.image.load(img_path)
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    return img

LEVEL_TIME = 3600

start_game = False


start_img = pygame.image.load("./src/img/start_btn.png").convert_alpha()
quit_img = pygame.image.load("./src/img/quit_btn.png").convert_alpha()
restart_img = pygame.image.load("./src/img/restart_btn.png").convert_alpha()
options_img = pygame.image.load("./src/img/options_btn.png").convert_alpha()


start_btn = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT -350, start_img, 0.5 )
options_btn = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT -250, options_img, 0.5 )
quit_btn = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT -150, quit_img, 0.5 )
restart_btn = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT -250, restart_img, 0.5 )


level1 = pygame.image.load("./src/img/level1.png").convert_alpha()
level2 = pygame.image.load("./src/img/level2.png").convert_alpha()
level3 = pygame.image.load("./src/img/level3.png").convert_alpha()

levels_btn = [ level1, level2, level3]


#define game variables
GRAVITY = 0.75

#define player action variables
moving_left = False
moving_right = False
shoot = False

#define colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255,255,255)
RESET_HIT_TIME = 2000


font = pygame.font.SysFont("Futura", 30)
font2 = pygame.font.SysFont("Futura", 48)

# Initialize the display
# Load images
health_box_img = pygame.image.load("./src/img/Utilities/life.png").convert_alpha()
ammo_box_img = pygame.image.load("./src/img/Utilities/ammo.png").convert_alpha()
coin_img = pygame.image.load("./src/img/Utilities/coin.png").convert_alpha()
diamond_img = pygame.image.load("./src/img/Utilities/diamond.png").convert_alpha()
star_img = pygame.image.load("./src/img/Utilities/star.png").convert_alpha()
item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Coin': coin_img,
    'Diamond': diamond_img,
    'Star': star_img
}

ROWS = 13
COLS = 24

def draw_text(text,font,text_col,x ,y):
    img = font.render(text, True, text_col)
    screen.blit(img,(x,y))


red = (255,0,0)
black = (0,0,0)



image_subir = pygame.image.load("./src/img/vol+.png")  # Reemplaza con tu imagen
image_bajar = pygame.image.load("./src/img/vol-.png")  # Reemplaza con tu imagen
image_mute = pygame.image.load("./src/img/mute.png")  # Reemplaza con tu imagen
image_unmute = pygame.image.load("./src/img/unmute.png")  # Reemplaza con tu imagen
image_resume = pygame.image.load("./src/img/resume.png")


button_Resume = Button(SCREEN_WIDTH // 2 - 120, 90, image_resume, 1.0)
button_subir = Button(500, 200, image_subir, 1.0)
button_bajar = Button(500, 300, image_bajar, 1.0)
button_mute = Button(700, 200, image_mute, 1.0)
button_unmute = Button(700, 300, image_unmute, 1.0)


coin_sound = pygame.mixer.Sound("./src/snd/coin.mp3")
coin_sound.set_volume(0.5)

uh_sound =pygame.mixer.Sound("./src/snd/daño.mp3")
uh_sound.set_volume(0.5)

laser_sound = pygame.mixer.Sound("./src/snd/laser.mp3")
laser_sound.set_volume(0.1)

enemy_sound = pygame.mixer.Sound("./src/snd/muerte.mp3")
enemy_sound.set_volume(0.6)

fireball_sound = pygame.mixer.Sound("./src/snd/fireball.mp3")
fireball_sound.set_volume(0.4)

hurt_sound = pygame.mixer.Sound("./src/snd/hurt.mp3")
hurt_sound.set_volume(0.2)

die_boss_sound = pygame.mixer.Sound("./src/snd/boss.mp3")
die_boss_sound.set_volume(0.3)

item_sound = pygame.mixer.Sound("./src/snd/item.mp3")
item_sound.set_volume(0.3)

win = pygame.mixer.Sound("./src/snd/win.mp3")
win.set_volume(0.3)

gameover = pygame.mixer.Sound("./src/snd/gameover.mp3")
gameover.set_volume(0.3)


LEVEL_BACKGROUND_IMAGES = [
    "./src/img/Background/0.png",
    "./src/img/Background/1.png",
    "./src/img/Background/2.png"
]
