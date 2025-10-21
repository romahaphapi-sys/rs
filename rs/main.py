import pygame 
import math
import sys
import random

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()

# Цвета
GRASS_COLOR = (60, 150, 60)
GROUND_COLOR = (150, 120, 90)
DARK_GREEN = (10, 70, 10)
TREE_GREEN = (20, 120, 20)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Путь - список точек (x, y)
PATH = [(0, 300), (200, 300), (400, 300), (600, 300), (800, 300)]

TOWER_IMG_SIZE = 80

try:
    tank_img = pygame.image.load("tank.png").convert_alpha()
    tank_img = pygame.transform.scale(tank_img, (40, 40))
except FileNotFoundError:
    tank_img = None

def load_tower_texture(level):
    filename = f"tower_push_{42 + (level - 1)}.png"
    try:
        img = pygame.image.load(filename).convert_alpha()
        img = pygame.transform.scale(img, (TOWER_IMG_SIZE, TOWER_IMG_SIZE))
        return img
    except FileNotFoundError:
        return None

class Enemy:
    def __init__(self, hp=100, speed=2, reward=50, size=40):
        self.x, self.y = PATH[0]
        self.speed = speed
        self.path_index = 0
        self.radius = size // 2
        self.max_hp = hp
        self.hp = hp
        self.reward = reward

    def move(self):
        if self.path_index + 1 >= len(PATH):
            return False
        target_x, target_y = PATH[self.path_index + 1]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed:
            self.x, self.y = target_x, target_y
            self.path_index += 1
        else:
            self.x += self.speed * dx / dist
            self.y += self.speed * dy / dist
        return True

    def draw(self):
        if tank_img:
            rect = tank_img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(tank_img, rect)
        else:
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)
        # Полоса здоровья
        hp_bar_len = 40
        pygame.draw.rect(screen, RED, (self.x - hp_bar_len//2, self.y - 25, hp_bar_len, 6))
        fill = (self.hp / self.max_hp) * hp_bar_len
        pygame.draw.rect(screen, (0, 255, 0), (self.x - hp_bar_len//2, self.y - 25, fill, 6))

class Tower:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.range = 120
        self.cooldown = 30
        self.timer = 0
        self.level = 1
        self.size = TOWER_IMG_SIZE
        self.upgrade_animation_timer = 0
        self.textures = {
            1: load_tower_texture(1),
            2: load_tower_texture(2),
            3: load_tower_texture(3)
        }

    def draw(self):
        img = self.textures.get(self.level)
        if img:
            rect = img.get_rect(center=(self.x, self.y))
            screen.blit(img, rect)
        else:
            pygame.draw.rect(screen, BLUE, (self.x - self.size//2, self.y - self.size//2, self.size, self.size))
        # Убрано свечение вокруг башни
        # if self.upgrade_animation_timer > 0:
        #     alpha = 255 * (self.upgrade_animation_timer / 20)
        #     flash_surface = pygame.Surface((self.range*2, self.range*2), pygame.SRCALPHA)
        #     pygame.draw.circle(flash_surface, (255, 255, 0, int(alpha)), (self.range, self.range), self.range, 4)
        #     screen.blit(flash_surface, (self.x - self.range, self.y - self.range))
        #     self.upgrade_animation_timer -= 1

    def can_shoot(self):
        return self.timer == 0

    def update_timer(self):
        if self.timer > 0:
            self.timer -= 1

    def attack(self, enemies, bullets):
        if self.timer > 0:
            self.timer -= 1
            return
        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.range and enemy.hp > 0:
                bullets.append(Bullet(self.x, self.y, enemy, damage=20 + 10 * (self.level - 1)))
                self.timer = self.cooldown
                break

    def upgrade(self):
        if self.level < 3:
            self.level += 1
            self.cooldown = max(10, self.cooldown - 3)
            self.upgrade_animation_timer = 20

    def upgrade_cost(self):
        return 50 + 30 * (self.level - 1)

class Bullet:
    def __init__(self, x, y, target, damage):
        self.x, self.y = x, y
        self.target = target
        self.speed = 7
        self.radius = 5
        self.active = True
        self.damage = damage

    def move(self):
        if not self.active or self.target.hp <= 0:
            self.active = False
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed:
            self.target.hp -= self.damage
            self.active = False
        else:
            self.x += self.speed * dx / dist
            self.y += self.speed * dy / dist

    def draw(self):
        if self.active:
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

def draw_grass():
    screen.fill(GRASS_COLOR)
    for _ in range(2000):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        pygame.draw.circle(screen, (80, 180, 80), (x, y), 1)

def draw_path():
    for i in range(len(PATH) - 1):
        pygame.draw.line(screen, GROUND_COLOR, PATH[i], PATH[i + 1], 40)

def draw_bushes():
    bush_positions = [
        (20, 20), (80, 40), (150, 30),
        (WIDTH - 60, 50), (WIDTH - 30, 20),
        (20, HEIGHT - 60), (60, HEIGHT - 30),
        (WIDTH - 80, HEIGHT - 40), (WIDTH - 40, HEIGHT - 20)
    ]
    for pos in bush_positions:
        pygame.draw.circle(screen, DARK_GREEN, pos, 15)

def draw_trees():
    tree_positions = [
        (50, 100), (120, 150), (180, 90),
        (WIDTH - 150, 120), (WIDTH - 100, 80),
        (50, HEIGHT - 150), (120, HEIGHT - 100),
        (WIDTH - 130, HEIGHT - 120), (WIDTH - 80, HEIGHT - 90)
    ]
    for pos in tree_positions:
        # Крона — круг с тенью
        crown_radius = random.randint(25, 40)
        pygame.draw.circle(screen, TREE_GREEN, pos, crown_radius)
        pygame.draw.circle(screen, (15, 90, 15), (pos[0] - 5, pos[1] - 5), crown_radius - 5)

def draw_gates():
    gate_width = 60
    gate_height = 80
    gate_thickness = 10
    arch_radius = 30

    start_x, start_y = PATH[0]
    gate_rect = pygame.Rect(start_x - gate_width//2, start_y - gate_height//2, gate_width, gate_height)
    pygame.draw.rect(screen, (120, 60, 0), gate_rect)
    pygame.draw.arc(screen, (80, 40, 0),
                    (start_x - arch_radius, start_y - gate_height//2 - arch_radius, arch_radius*2, arch_radius*2),
                    math.pi, 2*math.pi, gate_thickness)

    end_x, end_y = PATH[-1]
    gate_rect = pygame.Rect(end_x - gate_width//2, end_y - gate_height//2, gate_width, gate_height)
    pygame.draw.rect(screen, (120, 60, 0), gate_rect)
    pygame.draw.arc(screen, (80, 40, 0),
                    (end_x - arch_radius, end_y - gate_height//2 - arch_radius, arch_radius*2, arch_radius*2),
                    math.pi, 2*math.pi, gate_thickness)

def draw_text(text, size, x, y, color=WHITE):
    font = pygame.font.SysFont("Arial", size)
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))

def menu():
    menu_running = True
    font = pygame.font.SysFont("Arial", 50)
    while menu_running:
        draw_grass()
        draw_path()
        draw_gates()
        draw_bushes()
        draw_trees()

        title = font.render("Tower Defense", True, YELLOW)
        start_text = font.render("Нажмите Enter для старта", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                menu_running = False
        clock.tick(60)

def game_loop():
    money = 200
    lives = 10
    enemies = []
    towers = []
    bullets = []
    selected_tower = None

    wave_number = 1
    wave_max = 10
    enemies_per_wave = 10
    enemies_spawned = 0
    spawn_timer = 0
    spawn_delay = 30

    running = True
    while running:
        clock.tick(60)
        draw_grass()
        draw_path()
        draw_gates()
        draw_bushes()
        draw_trees()

        keys = pygame.key.get_pressed()
        ctrl_held = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                clicked_on_tower = False
                for tower in towers:
                    dist = math.hypot(tower.x - mx, tower.y - my)
                    if dist < tower.size // 2:
                        if ctrl_held:
                            towers.remove(tower)
                            if tower == selected_tower:
                                selected_tower = None
                        else:
                            selected_tower = tower
                        clicked_on_tower = True
                        break
                if not clicked_on_tower and not ctrl_held and money >= 100:
                    towers.append(Tower(mx, my))
                    money -= 100
                    selected_tower = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u and selected_tower:
                    cost = selected_tower.upgrade_cost()
                    if money >= cost:
                        money -= cost
                        selected_tower.upgrade()

        if wave_number <= wave_max:
            if enemies_spawned < enemies_per_wave:
                if spawn_timer <= 0:
                    hp = 120 + 10 * wave_number
                    speed = 2.0 + 0.1 * wave_number
                    reward = 70 + 10 * wave_number
                    enemies.append(Enemy(hp=hp, speed=speed, reward=reward))
                    enemies_spawned += 1
                    spawn_timer = spawn_delay
                else:
                    spawn_timer -= 1
            elif len(enemies) == 0:
                wave_number += 1
                enemies_spawned = 0
                spawn_timer = spawn_delay

        for enemy in enemies[:]:
            alive = enemy.move()
            if alive and enemy.hp > 0:
                enemy.draw()
            else:
                if enemy.hp <= 0:
                    money += enemy.reward
                else:
                    lives -= 1
                enemies.remove(enemy)

        for tower in towers:
            tower.update_timer()
            tower.attack(enemies, bullets)
            tower.draw()

        for bullet in bullets[:]:
            bullet.move()
            bullet.draw()
            if not bullet.active:
                bullets.remove(bullet)

        draw_text(f"Деньги: {money}", 25, 10, 10)
        draw_text(f"Жизни: {lives}", 25, 10, 40)
        draw_text(f"Волна: {min(wave_number, wave_max)} / {wave_max}", 25, 10, 70)

        if lives <= 0:
            draw_text("Игра окончена!", 60, WIDTH//2 - 150, HEIGHT//2 - 30, RED)
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False

        if wave_number > wave_max and len(enemies) == 0:
            draw_text("Поздравляем! Все волны пройдены!", 40, WIDTH//2 - 250, HEIGHT//2 - 20, YELLOW)
            pygame.display.flip()
            pygame.time.wait(4000)
            running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()

def main():
    menu()
    game_loop()

if __name__ == "__main__":
    main()
