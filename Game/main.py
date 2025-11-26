import pygame
import random
import math
import time

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TILE_SIZE = 50
FPS = 60
WORLD_WIDTH = 2000
WORLD_HEIGHT = 2000
INVENTORY_WIDTH = 5
INVENTORY_HEIGHT = 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRASS_GREEN = (34, 139, 34)
DARK_RED = (139, 0, 0)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
PURPLE = (128, 0, 128)
LIGHT_BLUE = (173, 216, 230)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Лесной Беглец")
clock = pygame.time.Clock()

class TextureManager:
    def __init__(self):
        self.grass_texture = None
        self.player_texture = None
        self.load_textures()
    
    def load_textures(self):
        try:
            self.grass_texture = pygame.image.load('grass.png').convert()
            self.grass_texture = pygame.transform.scale(self.grass_texture, (TILE_SIZE, TILE_SIZE))
        except:
            print("Не удалось загрузить текстуру травы grass.png. Будет использован зеленый фон.")
            self.grass_texture = None
        
        try:
            self.player_texture = pygame.image.load('player.png').convert_alpha()
            original_size = self.player_texture.get_size()
            scale_factor = (TILE_SIZE - 10) / max(original_size)
            new_width = int(original_size[0] * scale_factor)
            new_height = int(original_size[1] * scale_factor)
            self.player_texture = pygame.transform.scale(self.player_texture, (new_width, new_height))
        except:
            print("Не удалось загрузить текстуру персонажа player.png. Будет использован треугольник.")
            self.player_texture = None
    
    def draw_grass_background(self, screen, camera):
        if self.grass_texture:
            start_x = int(camera.x // TILE_SIZE) * TILE_SIZE
            start_y = int(camera.y // TILE_SIZE) * TILE_SIZE
            
            for x in range(start_x, start_x + SCREEN_WIDTH + TILE_SIZE, TILE_SIZE):
                for y in range(start_y, start_y + SCREEN_HEIGHT + TILE_SIZE, TILE_SIZE):
                    screen_x = x - camera.x
                    screen_y = y - camera.y
                    if -TILE_SIZE <= screen_x <= SCREEN_WIDTH and -TILE_SIZE <= screen_y <= SCREEN_HEIGHT:
                        screen.blit(self.grass_texture, (screen_x, screen_y))
        else:
            screen.fill(GRASS_GREEN)

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        
    def update(self, target):
        self.x = target.x - SCREEN_WIDTH // 2 + target.size // 2
        self.y = target.y - SCREEN_HEIGHT // 2 + target.size // 2
        self.x = max(0, min(self.x, WORLD_WIDTH - SCREEN_WIDTH))
        self.y = max(0, min(self.y, WORLD_HEIGHT - SCREEN_HEIGHT))
        
    def apply(self, entity):
        return entity.x - self.x, entity.y - self.y

class Player:
    def __init__(self, x, y, texture_manager):
        self.x = x
        self.y = y
        self.size = TILE_SIZE - 10
        self.speed = 4
        self.health = 100
        self.hunger = 100
        self.energy = 100
        self.direction = 0
        self.inventory = {'stick': 3, 'stone': 2, 'berry': 5, 'herb': 2, 'sword': 0, 'potion': 0}
        self.equipped = None
        self.texture_manager = texture_manager
        self.last_damage_time = 0
        self.damage_cooldown = 1000
        
    def move(self, dx, dy):
        if dx != 0 or dy != 0:
            self.direction = math.atan2(dy, dx)
            
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        if 0 <= new_x <= WORLD_WIDTH - self.size:
            self.x = new_x
        if 0 <= new_y <= WORLD_HEIGHT - self.size:
            self.y = new_y
            
    def take_damage(self, damage):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_damage_time > self.damage_cooldown:
            self.health = max(0, self.health - damage)
            self.last_damage_time = current_time
            return True
        return False
            
    def use_potion(self):
        if self.inventory.get('potion', 0) > 0:
            self.health = min(100, self.health + 40)
            self.inventory['potion'] -= 1
            return True
        return False
                
    def draw(self, screen, camera):
        screen_x, screen_y = camera.apply(self)
        
        if self.texture_manager.player_texture:
            rotated_texture = pygame.transform.rotate(self.texture_manager.player_texture, -math.degrees(self.direction))
            texture_rect = rotated_texture.get_rect(center=(screen_x + self.size // 2, screen_y + self.size // 2))
            screen.blit(rotated_texture, texture_rect)
        else:
            points = []
            front_x = screen_x + self.size // 2 + math.cos(self.direction) * self.size // 2
            front_y = screen_y + self.size // 2 + math.sin(self.direction) * self.size // 2
            back_left_x = screen_x + self.size // 2 + math.cos(self.direction + 2.5) * self.size // 2
            back_left_y = screen_y + self.size // 2 + math.sin(self.direction + 2.5) * self.size // 2
            back_right_x = screen_x + self.size // 2 + math.cos(self.direction - 2.5) * self.size // 2
            back_right_y = screen_y + self.size // 2 + math.sin(self.direction - 2.5) * self.size // 2
            
            points = [(front_x, front_y), (back_left_x, back_left_y), (back_right_x, back_right_y)]
            
            pygame.draw.polygon(screen, ORANGE, points)
            
            eye_size = self.size // 8
            eye_x = screen_x + self.size // 2 + math.cos(self.direction) * self.size // 3
            eye_y = screen_y + self.size // 2 + math.sin(self.direction) * self.size // 3
            pygame.draw.circle(screen, WHITE, (int(eye_x), int(eye_y)), eye_size)
            pygame.draw.circle(screen, BLACK, (int(eye_x), int(eye_y)), eye_size // 2)
        
        if self.equipped == 'sword':
            sword_length = self.size * 1.5
            sword_x = screen_x + self.size // 2 + math.cos(self.direction) * sword_length
            sword_y = screen_y + self.size // 2 + math.sin(self.direction) * sword_length
            pygame.draw.line(screen, GRAY, 
                           (screen_x + self.size // 2, screen_y + self.size // 2),
                           (sword_x, sword_y), 3)

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.size = TILE_SIZE - 10
        self.type = enemy_type
        self.speed = 2 if enemy_type == 'wolf' else 1.5
        self.health = 50
        self.damage = 15 if enemy_type == 'wolf' else 20
        self.color = RED if enemy_type == 'wolf' else BLUE
        self.direction = 0
        self.last_attack_time = 0
        self.attack_cooldown = 2000
        
    def update(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = max(1, math.sqrt(dx*dx + dy*dy))
        
        if dist < 400:
            dx, dy = dx/dist, dy/dist
            self.direction = math.atan2(dy, dx)
            self.x += dx * self.speed
            self.y += dy * self.speed
            
        if dist < TILE_SIZE:
            self.attack(player)
        
    def attack(self, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            if player.take_damage(self.damage):
                self.last_attack_time = current_time
        
    def draw(self, screen, camera):
        screen_x, screen_y = camera.apply(self)
        
        points = []
        front_x = screen_x + self.size // 2 + math.cos(self.direction) * self.size // 2
        front_y = screen_y + self.size // 2 + math.sin(self.direction) * self.size // 2
        back_left_x = screen_x + self.size // 2 + math.cos(self.direction + 2.5) * self.size // 2
        back_left_y = screen_y + self.size // 2 + math.sin(self.direction + 2.5) * self.size // 2
        back_right_x = screen_x + self.size // 2 + math.cos(self.direction - 2.5) * self.size // 2
        back_right_y = screen_y + self.size // 2 + math.sin(self.direction - 2.5) * self.size // 2
        
        points = [(front_x, front_y), (back_left_x, back_left_y), (back_right_x, back_right_y)]
        
        pygame.draw.polygon(screen, self.color, points)
        
        if self.health < 50:
            health_width = 40
            pygame.draw.rect(screen, DARK_RED, (screen_x, screen_y - 10, health_width, 5))
            pygame.draw.rect(screen, RED, (screen_x, screen_y - 10, health_width * (self.health / 50), 5))

class Resource:
    def __init__(self, x, y, res_type):
        self.x = x
        self.y = y
        self.size = TILE_SIZE - 15
        self.type = res_type
        self.colors = {
            'stick': BROWN,
            'stone': GRAY,
            'berry': RED,
            'herb': GREEN,
            'sword': PURPLE,
            'potion': LIGHT_BLUE
        }
        
    def draw(self, screen, camera):
        screen_x, screen_y = camera.apply(self)
        color = self.colors.get(self.type, WHITE)
        
        if self.type == 'sword':
            pygame.draw.line(screen, color, 
                           (screen_x, screen_y + self.size),
                           (screen_x + self.size, screen_y), 3)
        elif self.type == 'potion':
            # Рисуем зелье как колбу
            pygame.draw.rect(screen, color, (screen_x + 5, screen_y, self.size - 10, self.size))
            pygame.draw.rect(screen, DARK_GRAY, (screen_x + self.size//2 - 2, screen_y - 5, 4, 5))
        else:
            pygame.draw.rect(screen, color, (screen_x, screen_y, self.size, self.size))

class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        
    def draw(self, screen, camera):
        screen_x, screen_y = camera.apply(self)
        pygame.draw.rect(screen, BROWN, (screen_x + self.width//3, screen_y + self.height//2, 
                                        self.width//3, self.height//2))
        pygame.draw.circle(screen, DARK_GREEN, 
                          (screen_x + self.width//2, screen_y + self.height//3), 
                          self.width//2)

class Inventory:
    def __init__(self, player):
        self.player = player
        self.visible = False
        self.cell_size = 60
        self.width = INVENTORY_WIDTH * self.cell_size
        self.height = INVENTORY_HEIGHT * self.cell_size
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        self.crafting_recipes = {
            'sword': {'stone': 2, 'stick': 1},
            'potion': {'herb': 1}
        }
        
    def toggle(self):
        self.visible = not self.visible
        
    def draw(self, screen):
        if not self.visible:
            return
            
        pygame.draw.rect(screen, DARK_GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, LIGHT_GRAY, (self.x, self.y, self.width, self.height), 2)
        
        for i in range(INVENTORY_WIDTH + 1):
            pygame.draw.line(screen, LIGHT_GRAY, 
                           (self.x + i * self.cell_size, self.y),
                           (self.x + i * self.cell_size, self.y + self.height), 1)
        for i in range(INVENTORY_HEIGHT + 1):
            pygame.draw.line(screen, LIGHT_GRAY, 
                           (self.x, self.y + i * self.cell_size),
                           (self.x + self.width, self.y + i * self.cell_size), 1)
        
        items = list(self.player.inventory.items())
        for idx, (item_type, count) in enumerate(items):
            if count > 0:
                row = idx // INVENTORY_WIDTH
                col = idx % INVENTORY_WIDTH
                
                if row < INVENTORY_HEIGHT:
                    cell_x = self.x + col * self.cell_size + 5
                    cell_y = self.y + row * self.cell_size + 5
                    
                    colors = {
                        'stick': BROWN,
                        'stone': GRAY,
                        'berry': RED,
                        'herb': GREEN,
                        'sword': PURPLE,
                        'potion': LIGHT_BLUE
                    }
                    
                    color = colors.get(item_type, WHITE)
                    
                    if item_type == 'sword':
                        pygame.draw.line(screen, color, 
                                       (cell_x, cell_y + self.cell_size - 10),
                                       (cell_x + self.cell_size - 10, cell_y + 10), 3)
                    elif item_type == 'potion':
                        # Рисуем зелье в инвентаре
                        pygame.draw.rect(screen, color, (cell_x + 10, cell_y + 5, self.cell_size - 20, self.cell_size - 10))
                        pygame.draw.rect(screen, DARK_GRAY, (cell_x + self.cell_size//2 - 2, cell_y, 4, 5))
                    else:
                        pygame.draw.rect(screen, color, (cell_x, cell_y, self.cell_size - 10, self.cell_size - 10))
                    
                    count_text = pygame.font.SysFont('arial', 16).render(str(count), True, WHITE)
                    screen.blit(count_text, (cell_x + self.cell_size - 25, cell_y + self.cell_size - 20))
        
        recipe_y = self.y + self.height + 10
        recipe_text = pygame.font.SysFont('arial', 20).render("Рецепты крафта:", True, WHITE)
        screen.blit(recipe_text, (self.x, recipe_y))
        
        for recipe, ingredients in self.crafting_recipes.items():
            recipe_y += 25
            ingredient_text = f"{recipe}: "
            for item, count in ingredients.items():
                ingredient_text += f"{item} x{count} "
            
            can_craft = True
            for item, count in ingredients.items():
                if self.player.inventory.get(item, 0) < count:
                    can_craft = False
                    break
            
            color = GREEN if can_craft else RED
            text = pygame.font.SysFont('arial', 16).render(ingredient_text, True, color)
            screen.blit(text, (self.x, recipe_y))
            
            if can_craft:
                craft_rect = pygame.Rect(self.x + 200, recipe_y, 60, 20)
                pygame.draw.rect(screen, BLUE, craft_rect)
                craft_text = pygame.font.SysFont('arial', 14).render("Скрафтить", True, WHITE)
                screen.blit(craft_text, (craft_rect.x + 5, craft_rect.y + 2))
                
                mouse_pos = pygame.mouse.get_pos()
                if craft_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                    self.craft_item(recipe, ingredients)
    
    def craft_item(self, item, ingredients):
        for ingredient, count in ingredients.items():
            if self.player.inventory.get(ingredient, 0) < count:
                return False
        
        for ingredient, count in ingredients.items():
            self.player.inventory[ingredient] -= count
        
        self.player.inventory[item] = self.player.inventory.get(item, 0) + 1
        return True

class MiniMap:
    def __init__(self):
        self.width = 200
        self.height = 150
        self.x = SCREEN_WIDTH - self.width - 10
        self.y = 10
        self.border = 2
        
    def draw(self, screen, player, enemies, trees):
        pygame.draw.rect(screen, DARK_GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, LIGHT_GRAY, (self.x, self.y, self.width, self.height), self.border)
        
        scale_x = self.width / WORLD_WIDTH
        scale_y = self.height / WORLD_HEIGHT
        
        player_map_x = self.x + int(player.x * scale_x)
        player_map_y = self.y + int(player.y * scale_y)
        
        pygame.draw.circle(screen, ORANGE, (player_map_x, player_map_y), 4)
        
        for enemy in enemies:
            enemy_map_x = self.x + int(enemy.x * scale_x)
            enemy_map_y = self.y + int(enemy.y * scale_y)
            pygame.draw.circle(screen, enemy.color, (enemy_map_x, enemy_map_y), 3)
        
        for tree in trees[:50]:
            tree_map_x = self.x + int(tree.x * scale_x)
            tree_map_y = self.y + int(tree.y * scale_y)
            pygame.draw.circle(screen, DARK_GREEN, (tree_map_x, tree_map_y), 1)
        
        map_text = pygame.font.SysFont('arial', 12).render("Карта", True, WHITE)
        screen.blit(map_text, (self.x + self.width//2 - map_text.get_width()//2, self.y + self.height + 2))

class WaveManager:
    def __init__(self):
        self.current_wave = 0
        self.waves = [
            {"enemies_to_kill": 1, "description": "Волна 1: Убейте 15 врагов"},
            {"enemies_to_kill": 2, "description": "Волна 2: Убейте 25 врагов"},
            {"enemies_to_kill": 3, "description": "Финальная волна: Убейте 30 врагов"}
        ]
        self.enemies_killed = 0
        self.enemies_killed_this_wave = 0
        self.state = "between_waves"  # "active", "between_waves", "victory"
        self.wave_start_time = 0
        self.wave_end_time = 0
        self.rest_time = 15
        self.game_start_time = 0
        self.victory_time = 0
        
    def start_next_wave(self):
        if self.current_wave < len(self.waves):
            self.current_wave += 1
            self.enemies_killed_this_wave = 0
            self.state = "active"
            self.wave_start_time = time.time()
            return True
        return False
    
    def end_wave(self):
        self.state = "between_waves"
        self.wave_end_time = time.time()
    
    def check_victory(self):
        if self.current_wave == len(self.waves) and self.enemies_killed_this_wave >= self.waves[-1]["enemies_to_kill"]:
            self.state = "victory"
            self.victory_time = time.time()
            return True
        return False
    
    def get_remaining_rest_time(self):
        if self.state == "between_waves":
            elapsed = time.time() - self.wave_end_time
            remaining = max(0, self.rest_time - elapsed)
            return remaining
        return 0
    
    def should_spawn_enemies(self):
        return self.state == "active"
    
    def get_wave_info(self):
        if self.current_wave > 0 and self.current_wave <= len(self.waves):
            return self.waves[self.current_wave - 1]
        return None
    
    def get_total_game_time(self):
        if self.state == "victory":
            return self.victory_time - self.game_start_time
        return time.time() - self.game_start_time

class Game:
    def __init__(self):
        self.texture_manager = TextureManager()
        self.camera = Camera()
        self.player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2, self.texture_manager)
        self.inventory = Inventory(self.player)
        self.minimap = MiniMap()
        self.wave_manager = WaveManager()
        self.enemies = []
        self.resources = []
        self.trees = []
        self.game_state = "menu"
        self.last_enemy_spawn = 0
        self.enemy_spawn_cooldown = 2000
        self.show_warning = False
        self.damage_indicator = None
        self.damage_indicator_time = 0
        self.potion_effect_time = 0
        self.show_potion_effect = False
        self.generate_world()
        
    def generate_world(self):
        for _ in range(100):
            x = random.randint(0, WORLD_WIDTH - TILE_SIZE)
            y = random.randint(0, WORLD_HEIGHT - TILE_SIZE)
            self.trees.append(Tree(x, y))
            
        for _ in range(80):
            x = random.randint(0, WORLD_WIDTH - TILE_SIZE)
            y = random.randint(0, WORLD_HEIGHT - TILE_SIZE)
            res_type = random.choice(['stick', 'stone', 'berry', 'herb'])
            self.resources.append(Resource(x, y, res_type))
    
    def spawn_enemy(self):
        while True:
            x = random.randint(0, WORLD_WIDTH - TILE_SIZE)
            y = random.randint(0, WORLD_HEIGHT - TILE_SIZE)
            dist_to_player = math.sqrt((x - self.player.x)**2 + (y - self.player.y)**2)
            
            if dist_to_player > 300:
                enemy_type = random.choice(['wolf', 'soldier'])
                self.enemies.append(Enemy(x, y, enemy_type))
                break
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.game_state == "menu":
                        self.game_state = "playing"
                        self.wave_manager.game_start_time = time.time()
                        self.wave_manager.start_next_wave()
                    elif self.game_state == "victory":
                        self.__init__()
                    
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "playing":
                        if self.inventory.visible:
                            self.inventory.visible = False
                        else:
                            self.game_state = "paused"
                    elif self.game_state == "paused":
                        if self.show_warning:
                            self.show_warning = False
                        else:
                            self.game_state = "playing"
                    elif self.game_state == "menu":
                        return False
                        
                if event.key == pygame.K_i and self.game_state == "playing":
                    self.inventory.toggle()
                        
                if event.key == pygame.K_e and self.game_state == "playing" and not self.inventory.visible:
                    for resource in self.resources[:]:
                        dist = math.sqrt((self.player.x - resource.x)**2 + (self.player.y - resource.y)**2)
                        if dist < TILE_SIZE:
                            self.player.inventory[resource.type] = self.player.inventory.get(resource.type, 0) + 1
                            self.resources.remove(resource)
                            
                if event.key == pygame.K_1 and self.game_state == "playing" and not self.inventory.visible:
                    if self.player.inventory.get('stick', 0) >= 1:
                        self.player.equipped = 'stick'
                    
                if event.key == pygame.K_2 and self.game_state == "playing" and not self.inventory.visible:
                    if self.player.inventory.get('sword', 0) >= 1:
                        self.player.equipped = 'sword'
                    
                if event.key == pygame.K_r and self.game_state == "playing" and not self.inventory.visible:
                    if self.player.inventory.get('berry', 0) > 0:
                        self.player.hunger = min(100, self.player.hunger + 20)
                        self.player.inventory['berry'] -= 1
                        
                if event.key == pygame.K_h and self.game_state == "playing" and not self.inventory.visible:
                    if self.player.inventory.get('herb', 0) > 0:
                        self.player.health = min(100, self.player.health + 15)
                        self.player.inventory['herb'] -= 1
                        
                if event.key == pygame.K_p and self.game_state == "playing" and not self.inventory.visible:
                    if self.player.use_potion():
                        self.show_potion_effect = True
                        self.potion_effect_time = pygame.time.get_ticks()
                        self.damage_indicator = "+40 HP"
                        self.damage_indicator_time = pygame.time.get_ticks()
                        
                if event.key == pygame.K_SPACE and self.game_state == "playing" and not self.inventory.visible:
                    damage = 10
                    if self.player.equipped == 'sword':
                        damage = 25
                    
                    enemies_killed_this_attack = 0
                    for enemy in self.enemies[:]:
                        dist = math.sqrt((self.player.x - enemy.x)**2 + (self.player.y - enemy.y)**2)
                        if dist < TILE_SIZE * 1.5:
                            enemy.health -= damage
                            if enemy.health <= 0:
                                self.enemies.remove(enemy)
                                self.wave_manager.enemies_killed += 1
                                self.wave_manager.enemies_killed_this_wave += 1
                                enemies_killed_this_attack += 1
                    
                    if enemies_killed_this_attack > 0:
                        self.damage_indicator = f"+{enemies_killed_this_attack}"
                        self.damage_indicator_time = pygame.time.get_ticks()
                                
                if event.key == pygame.K_RETURN and self.game_state == "game_over":
                    self.__init__()
            
            if event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "paused" and self.show_warning:
                mouse_pos = pygame.mouse.get_pos()
                
                yes_button = pygame.Rect(SCREEN_WIDTH//2 - 120, 450, 100, 40)
                if yes_button.collidepoint(mouse_pos):
                    self.__init__()
                    self.game_state = "menu"
                    self.show_warning = False
                
                no_button = pygame.Rect(SCREEN_WIDTH//2 + 20, 450, 100, 40)
                if no_button.collidepoint(mouse_pos):
                    self.show_warning = False
                    
        return True
    
    def update(self):
        if self.game_state != "playing" or self.inventory.visible:
            return
            
        self.camera.update(self.player)
            
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
            
        if dx != 0 or dy != 0:
            self.player.move(dx, dy)
            
        for enemy in self.enemies:
            enemy.update(self.player)
        
        # Управление волнами
        if self.wave_manager.state == "active":
            current_wave = self.wave_manager.get_wave_info()
            if current_wave and self.wave_manager.enemies_killed_this_wave >= current_wave["enemies_to_kill"]:
                if self.wave_manager.current_wave == len(self.wave_manager.waves):
                    if self.wave_manager.check_victory():
                        self.game_state = "victory"
                else:
                    self.wave_manager.end_wave()
            
            # Спавн врагов во время активной волны
            if len(self.enemies) < 10:  # Максимум 10 врагов одновременно
                current_time = pygame.time.get_ticks()
                if current_time - self.last_enemy_spawn > self.enemy_spawn_cooldown:
                    self.spawn_enemy()
                    self.last_enemy_spawn = current_time
        
        elif self.wave_manager.state == "between_waves":
            remaining_time = self.wave_manager.get_remaining_rest_time()
            if remaining_time <= 0:
                self.wave_manager.start_next_wave()
            
        self.player.hunger = max(0, self.player.hunger - 0.05)
        self.player.energy = max(0, self.player.energy - 0.03)
        
        if self.player.hunger <= 0:
            self.player.health = max(0, self.player.health - 0.1)
            
        if self.damage_indicator and pygame.time.get_ticks() - self.damage_indicator_time > 500:
            self.damage_indicator = None
            
        if self.show_potion_effect and pygame.time.get_ticks() - self.potion_effect_time > 1000:
            self.show_potion_effect = False
            
        if self.player.health <= 0:
            self.game_state = "game_over"
    
    def draw(self):
        screen.fill(BLACK)
        
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "playing":
            self.draw_game()
            self.inventory.draw(screen)
            self.minimap.draw(screen, self.player, self.enemies, self.trees)
            self.draw_wave_info()
        elif self.game_state == "paused":
            self.draw_game()
            self.minimap.draw(screen, self.player, self.enemies, self.trees)
            self.draw_wave_info()
            if self.show_warning:
                self.draw_warning()
            else:
                self.draw_pause_menu()
        elif self.game_state == "game_over":
            self.draw_game()
            self.minimap.draw(screen, self.player, self.enemies, self.trees)
            self.draw_game_over()
        elif self.game_state == "victory":
            self.draw_game()
            self.minimap.draw(screen, self.player, self.enemies, self.trees)
            self.draw_victory_screen()
            
        pygame.display.flip()
    
    def draw_wave_info(self):
        wave_info = self.wave_manager.get_wave_info()
        if wave_info:
            # Информация о волне
            wave_text = pygame.font.SysFont('arial', 24).render(wave_info["description"], True, WHITE)
            screen.blit(wave_text, (SCREEN_WIDTH//2 - wave_text.get_width()//2, 50))
            
            # Прогресс волны
            progress_text = pygame.font.SysFont('arial', 20).render(
                f"Убито: {self.wave_manager.enemies_killed_this_wave}/{wave_info['enemies_to_kill']}", 
                True, GREEN)
            screen.blit(progress_text, (SCREEN_WIDTH//2 - progress_text.get_width()//2, 80))
            
            # Общее количество убийств
            total_kills_text = pygame.font.SysFont('arial', 18).render(
                f"Всего убито: {self.wave_manager.enemies_killed}", 
                True, LIGHT_GRAY)
            screen.blit(total_kills_text, (SCREEN_WIDTH//2 - total_kills_text.get_width()//2, 105))
        
        # Таймер отдыха между волнами
        if self.wave_manager.state == "between_waves":
            remaining_time = self.wave_manager.get_remaining_rest_time()
            rest_text = pygame.font.SysFont('arial', 28).render(
                f"Отдых: {int(remaining_time)} сек", 
                True, YELLOW)
            screen.blit(rest_text, (SCREEN_WIDTH//2 - rest_text.get_width()//2, 150))
            
            hint_text = pygame.font.SysFont('arial', 20).render(
                "Используйте это время для лечения и подготовки", 
                True, LIGHT_GRAY)
            screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, 185))
    
    def draw_menu(self):
        screen.fill(GRASS_GREEN)
        
        font_large = pygame.font.SysFont('arial', 60)
        title = font_large.render("ЛЕСНОЙ БЕГЛЕЦ", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        font_small = pygame.font.SysFont('arial', 30)
        instruction = font_small.render("Нажмите ENTER для начала игры", True, WHITE)
        screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, 300))
        
        controls = [
            "Управление:",
            "WASD - движение",
            "E - сбор ресурсов", 
            "SPACE - атака",
            "1 - экипировать палку",
            "2 - экипировать меч",
            "I - инвентарь и крафт",
            "R - съесть ягоды",
            "H - использовать траву",
            "P - выпить зелье",
            "ESC - пауза/меню"
        ]
        
        for i, text in enumerate(controls):
            control_text = pygame.font.SysFont('arial', 20).render(text, True, WHITE)
            screen.blit(control_text, (50, 400 + i * 30))
    
    def draw_game(self):
        self.texture_manager.draw_grass_background(screen, self.camera)
        
        for tree in self.trees:
            tree.draw(screen, self.camera)
            
        for resource in self.resources:
            resource.draw(screen, self.camera)
            
        for enemy in self.enemies:
            enemy.draw(screen, self.camera)
            
        self.player.draw(screen, self.camera)
        
        if self.damage_indicator:
            screen_x, screen_y = self.camera.apply(self.player)
            color = GREEN if "+" in self.damage_indicator else RED
            damage_text = pygame.font.SysFont('arial', 24).render(f"{self.damage_indicator}", True, color)
            screen.blit(damage_text, (screen_x + self.player.size // 2 - damage_text.get_width() // 2, 
                                    screen_y - 30))
        
        if self.show_potion_effect:
            screen_x, screen_y = self.camera.apply(self.player)
            effect_radius = 30
            pygame.draw.circle(screen, LIGHT_BLUE, 
                             (int(screen_x + self.player.size // 2), int(screen_y + self.player.size // 2)),
                             effect_radius, 2)
        
        self.draw_ui()
    
    def draw_ui(self):
        bar_width = 200
        bar_height = 20
        
        pygame.draw.rect(screen, RED, (10, 10, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (10, 10, bar_width * (self.player.health / 100), bar_height))
        health_text = pygame.font.SysFont('arial', 16).render(f"Здоровье: {int(self.player.health)}", True, WHITE)
        screen.blit(health_text, (15, 12))
        
        pygame.draw.rect(screen, RED, (10, 40, bar_width, bar_height))
        pygame.draw.rect(screen, YELLOW, (10, 40, bar_width * (self.player.hunger / 100), bar_height))
        hunger_text = pygame.font.SysFont('arial', 16).render(f"Сытость: {int(self.player.hunger)}", True, WHITE)
        screen.blit(hunger_text, (15, 42))
        
        pygame.draw.rect(screen, RED, (10, 70, bar_width, bar_height))
        pygame.draw.rect(screen, BLUE, (10, 70, bar_width * (self.player.energy / 100), bar_height))
        energy_text = pygame.font.SysFont('arial', 16).render(f"Энергия: {int(self.player.energy)}", True, WHITE)
        screen.blit(energy_text, (15, 72))
        
        inv_y = 100
        for item, count in self.player.inventory.items():
            if count > 0:
                inv_text = pygame.font.SysFont('arial', 16).render(f"{item}: {count}", True, WHITE)
                screen.blit(inv_text, (15, inv_y))
                inv_y += 25
                
        if self.player.equipped:
            equip_text = pygame.font.SysFont('arial', 16).render(f"Экипировано: {self.player.equipped}", True, WHITE)
            screen.blit(equip_text, (15, SCREEN_HEIGHT - 50))
        
        potion_count = self.player.inventory.get('potion', 0)
        potion_text = pygame.font.SysFont('arial', 16).render(f"Зелья: {potion_count} (P - использовать)", True, LIGHT_BLUE)
        screen.blit(potion_text, (15, SCREEN_HEIGHT - 30))
        
        if not self.inventory.visible:
            inv_hint = pygame.font.SysFont('arial', 14).render("Нажмите I для открытия инвентаря", True, LIGHT_GRAY)
            screen.blit(inv_hint, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 30))
    
    def draw_pause_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.SysFont('arial', 60)
        pause_text = font_large.render("ПАУЗА", True, WHITE)
        screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, 200))
        
        font_small = pygame.font.SysFont('arial', 30)
        instruction = font_small.render("Нажмите ESC для продолжения", True, WHITE)
        screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, 300))
        
        menu_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 400, 200, 50)
        pygame.draw.rect(screen, RED, menu_button)
        menu_text = pygame.font.SysFont('arial', 24).render("В главное меню", True, WHITE)
        screen.blit(menu_text, (menu_button.centerx - menu_text.get_width()//2, 
                              menu_button.centery - menu_text.get_height()//2))
        
        mouse_pos = pygame.mouse.get_pos()
        if menu_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (200, 0, 0), menu_button, 3)
            if pygame.mouse.get_pressed()[0]:
                self.show_warning = True
    
    def draw_warning(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        
        warning_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, 200, 500, 300)
        pygame.draw.rect(screen, DARK_GRAY, warning_rect)
        pygame.draw.rect(screen, RED, warning_rect, 3)
        
        font_large = pygame.font.SysFont('arial', 36)
        warning_title = font_large.render("ПРЕДУПРЕЖДЕНИЕ", True, RED)
        screen.blit(warning_title, (SCREEN_WIDTH//2 - warning_title.get_width()//2, 230))
        
        font_small = pygame.font.SysFont('arial', 24)
        warning_text = [
            "Вы уверены, что хотите вернуться",
            "в главное меню?",
            "",
            "Весь текущий прогресс будет потерян!",
            "Собранные ресурсы и созданные предметы",
            "будут сброшены."
        ]
        
        for i, text in enumerate(warning_text):
            text_surface = font_small.render(text, True, WHITE)
            screen.blit(text_surface, (SCREEN_WIDTH//2 - text_surface.get_width()//2, 300 + i * 30))
        
        yes_button = pygame.Rect(SCREEN_WIDTH//2 - 120, 450, 100, 40)
        pygame.draw.rect(screen, RED, yes_button)
        yes_text = pygame.font.SysFont('arial', 20).render("Да", True, WHITE)
        screen.blit(yes_text, (yes_button.centerx - yes_text.get_width()//2, 
                             yes_button.centery - yes_text.get_height()//2))
        
        no_button = pygame.Rect(SCREEN_WIDTH//2 + 20, 450, 100, 40)
        pygame.draw.rect(screen, GREEN, no_button)
        no_text = pygame.font.SysFont('arial', 20).render("Нет", True, WHITE)
        screen.blit(no_text, (no_button.centerx - no_text.get_width()//2, 
                            no_button.centery - no_text.get_height()//2))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.SysFont('arial', 60)
        game_over = font_large.render("ИГРА ОКОНЧЕНА", True, RED)
        screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, 250))
        
        font_small = pygame.font.SysFont('arial', 30)
        restart = font_small.render("Нажмите ENTER для новой игры", True, WHITE)
        screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 350))
    
    def draw_victory_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.SysFont('arial', 60)
        victory_text = font_large.render("ПОБЕДА!", True, GREEN)
        screen.blit(victory_text, (SCREEN_WIDTH//2 - victory_text.get_width()//2, 150))
        
        font_medium = pygame.font.SysFont('arial', 36)
        stats_text = font_medium.render("Статистика:", True, WHITE)
        screen.blit(stats_text, (SCREEN_WIDTH//2 - stats_text.get_width()//2, 230))
        
        total_time = self.wave_manager.get_total_game_time()
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        
        font_small = pygame.font.SysFont('arial', 28)
        stats = [
            f"Всего врагов убито: {self.wave_manager.enemies_killed}",
            f"Время прохождения: {minutes:02d}:{seconds:02d}",
            f"Завершено волн: {len(self.wave_manager.waves)}",
            "",
            "Вы успешно защитили лес!"
        ]
        
        for i, text in enumerate(stats):
            stat_text = font_small.render(text, True, WHITE)
            screen.blit(stat_text, (SCREEN_WIDTH//2 - stat_text.get_width()//2, 290 + i * 40))
        
        font_small = pygame.font.SysFont('arial', 24)
        restart_text = font_small.render("Нажмите ENTER для новой игры", True, YELLOW)
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 500))

def main():
    game = Game()
    running = True
    
    while running:
        running = game.handle_events()
        game.update()
        game.draw()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()
