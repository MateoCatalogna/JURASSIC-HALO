import pygame
from config import *

class Node(pygame.sprite.Sprite):
    def __init__(self, pos, status, icon_speed, image_index):
        super().__init__()
        self.frames = levels_btn
        self.frame_index = image_index
        self.image = self.frames[self.frame_index].copy()
        self.rect = self.image.get_rect(center=pos)
        self.detection_zone = pygame.Rect(self.rect.centerx - (icon_speed / 2), self.rect.centery - (icon_speed / 2),
                                          icon_speed, icon_speed)

class Icon(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.image = pygame.image.load("./src/img/Utilities/icon.png")
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.rect.center = self.pos

class Overworld:
    def __init__(self, start_level, max_level, surface, create_level):
        # setup 
        self.display_surface = surface 
        self.max_level = max_level
        self.current_level = start_level
        self.create_level = create_level

        # movement logic
        self.moving = False
        self.move_direction = pygame.math.Vector2(0,0)
        self.speed = 8

        # sprites 
        self.setup_nodes()
        self.setup_icon()

    def setup_nodes(self):
        self.nodes = pygame.sprite.Group()

        for index, node_data in enumerate(levels.values()):
            if index == 2:
                node_sprite = Node(node_data['node_pos'], 'available', self.speed, index)
            elif index <= self.max_level:
                node_sprite = Node(node_data['node_pos'], 'available', self.speed, index)
            else:
                node_sprite = Node(node_data['node_pos'], 'locked', self.speed, index)
            self.nodes.add(node_sprite)

    def draw_paths(self):
        points = [node['node_pos'] for index, node in enumerate(levels.values()) if index <= self.max_level]
        
        # Check if there are at least two points to draw a line
        if len(points) >= 2:
            pygame.draw.lines(self.display_surface, 'red', False, points, 6)
            
    def update_path(self, current_level, next_level):
        # Find the nodes corresponding to the current and next levels
        current_node = self.nodes.sprites()[current_level]
        next_node = self.nodes.sprites()[next_level]

        # Create a line (path) between the centers of the two nodes
        pygame.draw.line(self.display_surface, 'red', current_node.rect.center, next_node.rect.center, 6)


    def setup_icon(self):
        self.icon = pygame.sprite.GroupSingle()

        if isinstance(self.current_level, int) and 0 <= self.current_level < len(self.nodes.sprites()):
            icon_sprite = Icon(self.nodes.sprites()[self.current_level].rect.center)
            self.icon.add(icon_sprite)

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.moving:
            if keys[pygame.K_RIGHT] and isinstance(self.current_level, int) and self.current_level < self.max_level:
                self.move_direction = self.get_movement_data('next')
                self.current_level += 1
                self.moving = True
            elif keys[pygame.K_LEFT] and isinstance(self.current_level, int) and self.current_level > 0:
                self.move_direction = self.get_movement_data('previous')
                self.current_level -= 1
                self.moving = True
            elif keys[pygame.K_SPACE]:
                self.create_level(self.current_level)

    def get_movement_data(self, target):
        start = pygame.math.Vector2(self.nodes.sprites()[self.current_level].rect.center)
        
        if target == 'next': 
            end = pygame.math.Vector2(self.nodes.sprites()[self.current_level + 1].rect.center)
        else:
            end = pygame.math.Vector2(self.nodes.sprites()[self.current_level - 1].rect.center)

        return (end - start).normalize()

    def update_icon_pos(self):
        if self.moving and self.move_direction:
            self.icon.sprite.pos += self.move_direction * self.speed
            target_node = self.nodes.sprites()[self.current_level]
            if target_node.detection_zone.collidepoint(self.icon.sprite.pos):
                self.moving = False
                self.move_direction = pygame.math.Vector2(0,0)

    def run(self):
        self.input()
        self.update_icon_pos()
        
        # Update icon position before drawing
        self.icon.update()

        self.draw_paths()
        self.nodes.draw(self.display_surface)
        
        # Draw the icon after updating its position
        self.icon.draw(self.display_surface)

        pygame.display.flip()
