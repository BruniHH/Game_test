import pygame
import random
import math

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TILE_SIZE = 50
FPS = 60
WORLD_WIDTH = 2000
WORLD_HEIGHT = 2000
INVENTORY_WIDTH = 5
INVENTORY_HEIGHT = 2

# Цвета
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

# Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Лесной Беглец")
clock = pygame.time.Clock()

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        
    def update(self, target):
        # Камера следует за игроком, центрируя его
        self.x = target.x - SCREEN_WIDTH // 2 + target.size // 2
        self.y = target.y - SCREEN_HEIGHT // 2 + target.size // 2
        
        # Ограничения камеры
        self.x = max(0, min(self.x, WORLD_WIDTH - SCREEN_WIDTH))
        self.y = max(0, min(self.y, WORLD_HEIGHT - SCREEN_HEIGHT))
        
    def apply(self, entity):
        # Применяет смещение камеры к объекту
        return entity.x - self.x, entity.y - self.y

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = TILE_SIZE - 10
        self.speed = 4
        self.health = 100
        self.hunger = 100
        self.energy = 100
        self.direction = 0  # Угол направления в радианах
        self.inventory = {'stick': 3, 'stone': 2, 'berry': 5, 'herb': 2, 'sword': 0}
        self.equipped = None
        
    def move(self, dx, dy):
        # Обновляем направление движения
        if dx != 0 or dy != 0:
            self.direction = math.atan2(dy, dx)
            
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        # Проверка границ мира
        if 0 <= new_x <= WORLD_WIDTH - self.size:
            self.x = new_x
        if 0 <= new_y <= WORLD_HEIGHT - self.size:
            self.y = new_y
                
    def draw(self, screen, camera):
        screen_x, screen_y = camera.apply(self)
        
        # Рисуем треугольник, ориентированный по направлению движения
        points = []
        # Нос треугольника (впереди)
        front_x = screen_x + self.size // 2 + math.cos(self.direction) * self.size // 2
        front_y = screen_y + self.size // 2 + math.sin(self.direction) * self.size // 2
        # Задние точки треугольника
        back_left_x = screen_x + self.size // 2 + math.cos(self.direction + 2.5) * self.size // 2
        back_left_y = screen_y + self.size // 2 + math.sin(self.direction + 2.5) * self.size // 2
        back_right_x = screen_x + self.size // 2 + math.cos(self.direction - 2.5) * self.size // 2
        back_right_y = screen_y + self.size // 2 + math.sin(self.direction - 2.5) * self.size // 2
        
        points = [(front_x, front_y), (back_left_x, back_left_y), (back_right_x, back_right_y)]
        
        # Тело игрока (треугольник)
        pygame.draw.polygon(screen, ORANGE, points)
        
        # Глаз (на "носу" треугольника)
        eye_size = self.size // 8
        eye_x = screen_x + self.size // 2 + math.cos(self.direction) * self.size // 3
        eye_y = screen_y + self.size // 2 + math.sin(self.direction) * self.size // 3
        pygame.draw.circle(screen, WHITE, (int(eye_x), int(eye_y)), eye_size)
        pygame.draw.circle(screen, BLACK, (int(eye_x), int(eye_y)), eye_size // 2)
        
        # Если экипирован меч, рисуем его
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
        self.color = RED if enemy_type == 'wolf' else BLUE
        self.direction = 0
        
    def update(self, player):
        # ИИ преследования с обновлением направления
        dx = player.x - self.x
        dy = player.y - self.y
        dist = max(1, math.sqrt(dx*dx + dy*dy))
        
        if dist < 400:  # Дистанция обнаружения
            dx, dy = dx/dist, dy/dist
            self.direction = math.atan2(dy, dx)
            
            self.x += dx * self.speed
            self.y += dy * self.speed
        
    def draw(self, screen, camera):
        screen_x, screen_y = camera.apply(self)
        
        # Рисуем треугольник врага
        points = []
        front_x = screen_x + self.size // 2 + math.cos(self.direction) * self.size // 2
        front_y = screen_y + self.size // 2 + math.sin(self.direction) * self.size // 2
        back_left_x = screen_x + self.size // 2 + math.cos(self.direction + 2.5) * self.size // 2
        back_left_y = screen_y + self.size // 2 + math.sin(self.direction + 2.5) * self.size // 2
        back_right_x = screen_x + self.size // 2 + math.cos(self.direction - 2.5) * self.size // 2
        back_right_y = screen_y + self.size // 2 + math.sin(self.direction - 2.5) * self.size // 2
        
        points = [(front_x, front_y), (back_left_x, back_left_y), (back_right_x, back_right_y)]
        
        pygame.draw.polygon(screen, self.color, points)
        
        # Полоска здоровья
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
            'sword': PURPLE
        }
        
    def draw(self, screen, camera):
        screen_x, screen_y = camera.apply(self)
        color = self.colors.get(self.type, WHITE)
        
        if self.type == 'sword':
            # Рисуем меч как линию
            pygame.draw.line(screen, color, 
                           (screen_x, screen_y + self.size),
                           (screen_x + self.size, screen_y), 3)
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
        
        # Ствол
        pygame.draw.rect(screen, BROWN, (screen_x + self.width//3, screen_y + self.height//2, 
                                        self.width//3, self.height//2))
        # Крона
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
            'sword': {'stone': 2, 'stick': 1}
        }
        
    def toggle(self):
        self.visible = not self.visible
        
    def draw(self, screen):
        if not self.visible:
            return
            
        # Фон инвентаря
        pygame.draw.rect(screen, DARK_GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, LIGHT_GRAY, (self.x, self.y, self.width, self.height), 2)
        
        # Рисуем сетку
        for i in range(INVENTORY_WIDTH + 1):
            pygame.draw.line(screen, LIGHT_GRAY, 
                           (self.x + i * self.cell_size, self.y),
                           (self.x + i * self.cell_size, self.y + self.height), 1)
        for i in range(INVENTORY_HEIGHT + 1):
            pygame.draw.line(screen, LIGHT_GRAY, 
                           (self.x, self.y + i * self.cell_size),
                           (self.x + self.width, self.y + i * self.cell_size), 1)
        
        # Заполняем инвентарь предметами
        items = list(self.player.inventory.items())
        for idx, (item_type, count) in enumerate(items):
            if count > 0:
                row = idx // INVENTORY_WIDTH
                col = idx % INVENTORY_WIDTH
                
                if row < INVENTORY_HEIGHT:  # Проверяем, чтобы не выйти за границы
                    cell_x = self.x + col * self.cell_size + 5
                    cell_y = self.y + row * self.cell_size + 5
                    
                    # Рисуем предмет
                    colors = {
                        'stick': BROWN,
                        'stone': GRAY,
                        'berry': RED,
                        'herb': GREEN,
                        'sword': PURPLE
                    }
                    
                    color = colors.get(item_type, WHITE)
                    
                    if item_type == 'sword':
                        # Рисуем меч
                        pygame.draw.line(screen, color, 
                                       (cell_x, cell_y + self.cell_size - 10),
                                       (cell_x + self.cell_size - 10, cell_y + 10), 3)
                    else:
                        pygame.draw.rect(screen, color, (cell_x, cell_y, self.cell_size - 10, self.cell_size - 10))
                    
                    # Количество предметов
                    count_text = pygame.font.SysFont('arial', 16).render(str(count), True, WHITE)
                    screen.blit(count_text, (cell_x + self.cell_size - 25, cell_y + self.cell_size - 20))
        
        # Отображаем рецепты крафта
        recipe_y = self.y + self.height + 10
        recipe_text = pygame.font.SysFont('arial', 20).render("Рецепты крафта:", True, WHITE)
        screen.blit(recipe_text, (self.x, recipe_y))
        
        for recipe, ingredients in self.crafting_recipes.items():
            recipe_y += 25
            ingredient_text = f"{recipe}: "
            for item, count in ingredients.items():
                ingredient_text += f"{item} x{count} "
            
            # Проверяем, можно ли скрафтить
            can_craft = True
            for item, count in ingredients.items():
                if self.player.inventory.get(item, 0) < count:
                    can_craft = False
                    break
            
            color = GREEN if can_craft else RED
            text = pygame.font.SysFont('arial', 16).render(ingredient_text, True, color)
            screen.blit(text, (self.x, recipe_y))
            
            # Кнопка крафта
            if can_craft:
                craft_rect = pygame.Rect(self.x + 200, recipe_y, 60, 20)
                pygame.draw.rect(screen, BLUE, craft_rect)
                craft_text = pygame.font.SysFont('arial', 14).render("Скрафтить", True, WHITE)
                screen.blit(craft_text, (craft_rect.x + 5, craft_rect.y + 2))
                
                # Обработка клика по кнопке крафта
                mouse_pos = pygame.mouse.get_pos()
                if craft_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                    self.craft_item(recipe, ingredients)
    
    def craft_item(self, item, ingredients):
        # Проверяем еще раз наличие ресурсов
        for ingredient, count in ingredients.items():
            if self.player.inventory.get(ingredient, 0) < count:
                return False
        
        # Убираем ресурсы
        for ingredient, count in ingredients.items():
            self.player.inventory[ingredient] -= count
        
        # Добавляем предмет
        self.player.inventory[item] = self.player.inventory.get(item, 0) + 1
        return True

class Game:
    def __init__(self):
        self.camera = Camera()
        self.player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        self.inventory = Inventory(self.player)
        self.enemies = []
        self.resources = []
        self.trees = []
        self.game_state = "menu"  # menu, playing, paused, game_over
        self.last_enemy_spawn = 0
        self.enemy_spawn_cooldown = 5000  # 5 секунд
        self.show_warning = False  # Флаг для показа предупреждения
        self.generate_world()
        
    def generate_world(self):
        # Генерация деревьев
        for _ in range(100):
            x = random.randint(0, WORLD_WIDTH - TILE_SIZE)
            y = random.randint(0, WORLD_HEIGHT - TILE_SIZE)
            self.trees.append(Tree(x, y))
            
        # Генерация ресурсов
        for _ in range(80):
            x = random.randint(0, WORLD_WIDTH - TILE_SIZE)
            y = random.randint(0, WORLD_HEIGHT - TILE_SIZE)
            res_type = random.choice(['stick', 'stone', 'berry', 'herb'])
            self.resources.append(Resource(x, y, res_type))
            
        # Начальные враги
        for _ in range(10):
            self.spawn_enemy()
    
    def spawn_enemy(self):
        # Спавн врага на расстоянии от игрока
        while True:
            x = random.randint(0, WORLD_WIDTH - TILE_SIZE)
            y = random.randint(0, WORLD_HEIGHT - TILE_SIZE)
            dist_to_player = math.sqrt((x - self.player.x)**2 + (y - self.player.y)**2)
            
            if dist_to_player > 300:  # Не спавнить слишком близко к игроку
                enemy_type = random.choice(['wolf', 'soldier'])
                self.enemies.append(Enemy(x, y, enemy_type))
                break
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.game_state == "menu":
                    self.game_state = "playing"
                    
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
                    # Сбор ресурсов
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
                        
                if event.key == pygame.K_SPACE and self.game_state == "playing" and not self.inventory.visible:
                    # Атака
                    damage = 10
                    if self.player.equipped == 'sword':
                        damage = 25
                    
                    for enemy in self.enemies[:]:
                        dist = math.sqrt((self.player.x - enemy.x)**2 + (self.player.y - enemy.y)**2)
                        if dist < TILE_SIZE * 1.5:
                            enemy.health -= damage
                            if enemy.health <= 0:
                                self.enemies.remove(enemy)
                                
                if event.key == pygame.K_RETURN and self.game_state == "game_over":
                    self.__init__()
            
            if event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "paused" and self.show_warning:
                mouse_pos = pygame.mouse.get_pos()
                
                # Проверка клика по кнопке "Да"
                yes_button = pygame.Rect(SCREEN_WIDTH//2 - 120, 450, 100, 40)
                if yes_button.collidepoint(mouse_pos):
                    self.__init__()  # Сброс игры
                    self.game_state = "menu"
                    self.show_warning = False
                
                # Проверка клика по кнопке "Нет"
                no_button = pygame.Rect(SCREEN_WIDTH//2 + 20, 450, 100, 40)
                if no_button.collidepoint(mouse_pos):
                    self.show_warning = False
                    
        return True
    
    def update(self):
        if self.game_state != "playing" or self.inventory.visible:
            return
            
        # Обновление камеры
        self.camera.update(self.player)
            
        # Обработка непрерывного движения
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
            
        # Применяем движение
        if dx != 0 or dy != 0:
            self.player.move(dx, dy)
            
        # Обновление врагов
        for enemy in self.enemies:
            enemy.update(self.player)
            
        # Спавн новых врагов
        current_time = pygame.time.get_ticks()
        if current_time - self.last_enemy_spawn > self.enemy_spawn_cooldown and len(self.enemies) < 20:
            self.spawn_enemy()
            self.last_enemy_spawn = current_time
            
        # Постепенное уменьшение характеристик
        self.player.hunger = max(0, self.player.hunger - 0.05)
        self.player.energy = max(0, self.player.energy - 0.03)
        
        if self.player.hunger <= 0:
            self.player.health = max(0, self.player.health - 0.1)
            
        # Проверка смерти
        if self.player.health <= 0:
            self.game_state = "game_over"
    
    def draw(self):
        screen.fill(BLACK)
        
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "playing":
            self.draw_game()
            self.inventory.draw(screen)
        elif self.game_state == "paused":
            self.draw_game()
            if self.show_warning:
                self.draw_warning()
            else:
                self.draw_pause_menu()
        elif self.game_state == "game_over":
            self.draw_game()
            self.draw_game_over()
            
        pygame.display.flip()
    
    def draw_menu(self):
        # Простой зеленый фон
        screen.fill(GRASS_GREEN)
        
        # Название игры
        font_large = pygame.font.SysFont('arial', 60)
        title = font_large.render("Таинственный лес", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        # Инструкция
        font_small = pygame.font.SysFont('arial', 30)
        instruction = font_small.render("Нажмите ENTER для начала игры", True, WHITE)
        screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, 300))
        
        # Управление
        controls = [
            "Управление:",
            "WASD - движение",
            "E - сбор ресурсов", 
            "SPACE - атака",
            "1 - экипировать палку",
            "2 - экипировать меч",
            "I - инвентарь и крафт",
            "R - съесть ягоды",
            "H - использовать травы",
            "ESC - пауза/меню"
        ]
        
        for i, text in enumerate(controls):
            control_text = pygame.font.SysFont('arial', 20).render(text, True, WHITE)
            screen.blit(control_text, (50, 400 + i * 30))
    
    def draw_game(self):
        # Простой зеленый фон для травы
        screen.fill(GRASS_GREEN)
        
        # Рисование деревьев
        for tree in self.trees:
            tree.draw(screen, self.camera)
            
        # Рисование ресурсов
        for resource in self.resources:
            resource.draw(screen, self.camera)
            
        # Рисование врагов
        for enemy in self.enemies:
            enemy.draw(screen, self.camera)
            
        # Рисование игрока
        self.player.draw(screen, self.camera)
        
        # Рисование UI
        self.draw_ui()
    
    def draw_ui(self):
        # Полоски статусов
        bar_width = 200
        bar_height = 20
        
        # Здоровье
        pygame.draw.rect(screen, RED, (10, 10, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (10, 10, bar_width * (self.player.health / 100), bar_height))
        health_text = pygame.font.SysFont('arial', 16).render(f"Здоровье: {int(self.player.health)}", True, WHITE)
        screen.blit(health_text, (15, 12))
        
        # Сытость
        pygame.draw.rect(screen, RED, (10, 40, bar_width, bar_height))
        pygame.draw.rect(screen, YELLOW, (10, 40, bar_width * (self.player.hunger / 100), bar_height))
        hunger_text = pygame.font.SysFont('arial', 16).render(f"Сытость: {int(self.player.hunger)}", True, WHITE)
        screen.blit(hunger_text, (15, 42))
        
        # Энергия
        pygame.draw.rect(screen, RED, (10, 70, bar_width, bar_height))
        pygame.draw.rect(screen, BLUE, (10, 70, bar_width * (self.player.energy / 100), bar_height))
        energy_text = pygame.font.SysFont('arial', 16).render(f"Энергия: {int(self.player.energy)}", True, WHITE)
        screen.blit(energy_text, (15, 72))
        
        # Инвентарь (упрощенный)
        inv_y = 100
        for item, count in self.player.inventory.items():
            if count > 0:
                inv_text = pygame.font.SysFont('arial', 16).render(f"{item}: {count}", True, WHITE)
                screen.blit(inv_text, (15, inv_y))
                inv_y += 25
                
        # Экипировка
        if self.player.equipped:
            equip_text = pygame.font.SysFont('arial', 16).render(f"Экипировано: {self.player.equipped}", True, WHITE)
            screen.blit(equip_text, (15, SCREEN_HEIGHT - 30))
        
        # Количество врагов
        enemy_text = pygame.font.SysFont('arial', 16).render(f"Врагов: {len(self.enemies)}", True, WHITE)
        screen.blit(enemy_text, (SCREEN_WIDTH - 120, 10))
        
        # Подсказка про инвентарь
        if not self.inventory.visible:
            inv_hint = pygame.font.SysFont('arial', 14).render("Нажмите I для открытия инвентаря", True, LIGHT_GRAY)
            screen.blit(inv_hint, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 30))
    
    def draw_pause_menu(self):
        # Затемнение
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.SysFont('arial', 60)
        pause_text = font_large.render("ПАУЗА", True, WHITE)
        screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, 200))
        
        font_small = pygame.font.SysFont('arial', 30)
        instruction = font_small.render("Нажмите ESC для продолжения", True, WHITE)
        screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, 300))
        
        # Кнопка возврата в главное меню
        menu_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 400, 200, 50)
        pygame.draw.rect(screen, RED, menu_button)
        menu_text = pygame.font.SysFont('arial', 24).render("В главное меню", True, WHITE)
        screen.blit(menu_text, (menu_button.centerx - menu_text.get_width()//2, 
                              menu_button.centery - menu_text.get_height()//2))
        
        # Обработка клика по кнопке
        mouse_pos = pygame.mouse.get_pos()
        if menu_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (200, 0, 0), menu_button, 3)  # Подсветка при наведении
            if pygame.mouse.get_pressed()[0]:
                self.show_warning = True
    
    def draw_warning(self):
        # Затемнение
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        
        # Фон предупреждения
        warning_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, 200, 500, 300)
        pygame.draw.rect(screen, DARK_GRAY, warning_rect)
        pygame.draw.rect(screen, RED, warning_rect, 3)
        
        # Текст предупреждения
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
        
        # Кнопка "Да"
        yes_button = pygame.Rect(SCREEN_WIDTH//2 - 120, 450, 100, 40)
        pygame.draw.rect(screen, RED, yes_button)
        yes_text = pygame.font.SysFont('arial', 20).render("Да", True, WHITE)
        screen.blit(yes_text, (yes_button.centerx - yes_text.get_width()//2, 
                             yes_button.centery - yes_text.get_height()//2))
        
        # Кнопка "Нет"
        no_button = pygame.Rect(SCREEN_WIDTH//2 + 20, 450, 100, 40)
        pygame.draw.rect(screen, GREEN, no_button)
        no_text = pygame.font.SysFont('arial', 20).render("Нет", True, WHITE)
        screen.blit(no_text, (no_button.centerx - no_text.get_width()//2, 
                            no_button.centery - no_text.get_height()//2))
    
    def draw_game_over(self):
        # Затемнение
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.SysFont('arial', 60)
        game_over = font_large.render("ИГРА ОКОНЧЕНА", True, RED)
        screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, 250))
        
        font_small = pygame.font.SysFont('arial', 30)
        restart = font_small.render("Нажмите ENTER для новой игры", True, WHITE)
        screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 350))

# Запуск игры
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
