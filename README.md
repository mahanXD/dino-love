import pygame
import random
import sys
import math
import json
import os

# Initialize
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Love - Amirhossein")
clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.Font(None, 24)
font_medium = pygame.font.Font(None, 40)
font_large = pygame.font.Font(None, 60)
font_huge = pygame.font.Font(None, 80)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 150, 0)
BROWN = (100, 50, 20)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)
PINK = (255, 100, 150)
YELLOW = (255, 255, 0)
BLUE = (50, 150, 255)
GOLD = (255, 215, 0)

# Game variables
GRAVITY = 0.7
JUMP_STRENGTH = -12
SCROLL_SPEED = 6
TARGET_DISTANCE = 2000
FULLSCREEN = False

# Game state
state = "RUNNING"
distance = 0
cutscene_step = 0
step_timer = 0

# ----------------------------------------------------------------------
# کلاس مدیریت ذخیره‌سازی
# ----------------------------------------------------------------------
class SaveManager:
    SAVE_FILE = "save.json"
    
    @staticmethod
    def save(win_count, max_jumps, double_jump_unlocked):
        data = {
            "win_count": win_count,
            "max_jumps": max_jumps,
            "double_jump_unlocked": double_jump_unlocked
        }
        try:
            with open(SaveManager.SAVE_FILE, "w") as f:
                json.dump(data, f)
            return True
        except:
            return False
    
    @staticmethod
    def load():
        if not os.path.exists(SaveManager.SAVE_FILE):
            return None
        try:
            with open(SaveManager.SAVE_FILE, "r") as f:
                return json.load(f)
        except:
            return None

# ----------------------------------------------------------------------
# کلاس مدیریت متغیرهای سراسری (با قابلیت لود از سیو)
# ----------------------------------------------------------------------
class GameData:
    MAX_JUMPS = 1
    win_count = 0
    DOUBLE_JUMP_UNLOCKED = False
    
    @classmethod
    def load_from_save(cls):
        data = SaveManager.load()
        if data:
            cls.win_count = data.get("win_count", 0)
            cls.DOUBLE_JUMP_UNLOCKED = data.get("double_jump_unlocked", False)
            cls.MAX_JUMPS = data.get("max_jumps", 1)
            return True
        return False
    
    @classmethod
    def save_progress(cls):
        return SaveManager.save(cls.win_count, cls.MAX_JUMPS, cls.DOUBLE_JUMP_UNLOCKED)

# لود سیو در ابتدای بازی
GameData.load_from_save()

# Dino Class
class Dino:
    def __init__(self):
        self.x = 80
        self.y = HEIGHT - 60
        self.width = 30
        self.height = 40
        self.y_vel = 0
        self.jumping = False
        self.dead = False
        self.jumps_used = 0

    def jump(self):
        if not self.dead:
            if self.jumps_used < GameData.MAX_JUMPS:
                self.y_vel = JUMP_STRENGTH
                self.jumping = True
                self.jumps_used += 1

    def update(self):
        if self.dead:
            return
        self.y += self.y_vel
        self.y_vel += GRAVITY
        if self.y >= HEIGHT - 60:
            self.y = HEIGHT - 60
            self.y_vel = 0
            self.jumping = False
            self.jumps_used = 0

    def draw(self, screen, sad=False, dead=False):
        color = (50, 50, 50) if not dead else (80, 80, 80)
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, color, (self.x + self.width - 10, self.y - 15, 15, 15))
        
        if dead:
            pygame.draw.line(screen, BLACK, (self.x + self.width - 8, self.y - 8), (self.x + self.width - 2, self.y - 8), 2)
            pygame.draw.line(screen, color, (self.x + 5, self.y + self.height), (self.x - 5, self.y + self.height + 10), 5)
            pygame.draw.line(screen, color, (self.x + self.width - 5, self.y + self.height), (self.x + self.width + 5, self.y + self.height + 10), 5)
        else:
            if sad:
                pygame.draw.circle(screen, WHITE, (self.x + self.width - 5, self.y - 10), 3)
                pygame.draw.circle(screen, BLACK, (self.x + self.width - 3, self.y - 10), 1)
                pygame.draw.line(screen, BLACK, (self.x + self.width - 10, self.y - 18), (self.x + self.width - 3, self.y - 18), 2)
            else:
                pygame.draw.circle(screen, WHITE, (self.x + self.width - 5, self.y - 10), 3)
                pygame.draw.circle(screen, BLACK, (self.x + self.width - 3, self.y - 10), 1)
            if not self.jumping:
                pygame.draw.line(screen, color, (self.x + 5, self.y + self.height), (self.x + 10, self.y + self.height + 15), 5)
                pygame.draw.line(screen, color, (self.x + self.width - 5, self.y + self.height), (self.x + self.width - 10, self.y + self.height + 15), 5)
            if GameData.MAX_JUMPS == 2 and not self.dead:
                remaining = GameData.MAX_JUMPS - self.jumps_used
                if remaining > 0:
                    for i in range(remaining):
                        pygame.draw.circle(screen, GOLD, (self.x - 10 - i*12, self.y - 5), 4)

    def draw_with_clothes(self, screen, is_bride=False):
        color = (50, 50, 50)
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, color, (self.x + self.width - 10, self.y - 15, 15, 15))
        pygame.draw.circle(screen, WHITE, (self.x + self.width - 5, self.y - 10), 3)
        pygame.draw.circle(screen, BLACK, (self.x + self.width - 3, self.y - 10), 1)

        if is_bride:
            pygame.draw.rect(screen, WHITE, (self.x - 5, self.y + 10, self.width + 10, 20))
            pygame.draw.rect(screen, WHITE, (self.x - 2, self.y - 25, 10, 15))
            pygame.draw.line(screen, WHITE, (self.x, self.y - 25), (self.x + 15, self.y - 30), 2)
        else:
            pygame.draw.rect(screen, (30, 30, 80), (self.x - 2, self.y - 5, self.width + 4, 20))
            pygame.draw.polygon(screen, RED, [(self.x + 10, self.y - 5), (self.x + 15, self.y + 5), (self.x + 20, self.y - 5)])

    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 5)

# Cactus Class
class Cactus:
    def __init__(self, x):
        self.width = 20
        self.height = random.randint(35, 55)
        self.x = x
        self.y = HEIGHT - 20 - self.height

    def update(self):
        self.x -= SCROLL_SPEED

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, GREEN, (self.x - 6, self.y + 10, 8, 8))
        pygame.draw.rect(screen, GREEN, (self.x + self.width - 2, self.y + 20, 8, 8))
        pygame.draw.rect(screen, GREEN, (self.x - 4, self.y + 30, 6, 6))

    def get_rect(self):
        return pygame.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 4)

# Bird Class
class Bird:
    def __init__(self, x):
        self.width = 30
        self.height = 20
        self.x = x
        self.base_y = random.choice([HEIGHT - 180, HEIGHT - 220, HEIGHT - 260])
        self.y = self.base_y
        self.wing_up = True
        self.timer = 0
        self.wave_offset = random.randint(0, 100)

    def update(self):
        self.x -= SCROLL_SPEED
        self.timer += 1
        if self.timer > 8:
            self.wing_up = not self.wing_up
            self.timer = 0
        self.y = self.base_y + 3 * math.sin(self.wave_offset * 0.05)
        self.wave_offset += 1

    def draw(self, screen):
        pygame.draw.ellipse(screen, BLUE, (self.x, self.y, self.width, self.height))
        if self.wing_up:
            pygame.draw.polygon(screen, BLUE, [(self.x + 5, self.y), (self.x + 15, self.y - 15), (self.x + 25, self.y)])
        else:
            pygame.draw.polygon(screen, BLUE, [(self.x + 5, self.y + self.height), (self.x + 15, self.y + self.height + 15), (self.x + 25, self.y + self.height)])
        pygame.draw.circle(screen, WHITE, (self.x + 25, self.y + 5), 3)
        pygame.draw.circle(screen, BLACK, (self.x + 26, self.y + 5), 1)

    def get_rect(self):
        return pygame.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 4)

# Drawing functions
def draw_ground():
    pygame.draw.rect(screen, BROWN, (0, HEIGHT - 20, WIDTH, 20))
    pygame.draw.line(screen, BLACK, (0, HEIGHT - 20), (WIDTH, HEIGHT - 20), 2)

def draw_text(text, font, color, x, y, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(img, rect)

def draw_cutscene(step, timer):
    screen.fill(DARK_GRAY)
    
    if step == 0:
        draw_text("Amirhossein started running after his love...", font_medium, WHITE, WIDTH//2, 50, center=True)
        dino = Dino()
        dino.x = 200
        dino.y = HEIGHT - 120
        dino.draw(screen)
        draw_ground()
        draw_text("Press ENTER to continue", font_small, YELLOW, WIDTH//2, HEIGHT - 30, center=True)

    elif step == 1:
        draw_text("Amirhossein arrived, but saw his love marrying someone else!", font_medium, WHITE, WIDTH//2, 30, center=True)
        bride = Dino()
        bride.x = 600
        bride.y = HEIGHT - 120
        bride.draw_with_clothes(screen, is_bride=True)
        groom = Dino()
        groom.x = 500
        groom.y = HEIGHT - 120
        groom.draw_with_clothes(screen, is_bride=False)
        main_dino = Dino()
        main_dino.x = 150
        main_dino.y = HEIGHT - 120
        main_dino.draw(screen, sad=True)
        draw_text("💔", font_huge, RED, 400, 150, center=True)
        draw_ground()
        draw_text("Press ENTER to continue", font_small, YELLOW, WIDTH//2, HEIGHT - 30, center=True)

    elif step == 2:
        draw_text("Heartbroken, Amirhossein crashed into a cactus...", font_medium, RED, WIDTH//2, 30, center=True)
        big_cactus = Cactus(WIDTH // 2 + 50)
        big_cactus.height = 80
        big_cactus.y = HEIGHT - 20 - 80
        big_cactus.draw(screen)
        dino = Dino()
        dino.x = WIDTH // 2 + 20
        dino.y = HEIGHT - 120
        dino.draw(screen)
        for i in range(5):
            x = WIDTH//2 + 80 + random.randint(-20, 20)
            y = HEIGHT//2 + random.randint(-30, 30)
            pygame.draw.line(screen, YELLOW, (x, y), (x+20, y-20), 3)
        draw_ground()
        draw_text("Press ENTER to continue", font_small, YELLOW, WIDTH//2, HEIGHT - 30, center=True)

    elif step >= 3:
        screen.fill((30, 0, 0))
        draw_text("💔 Amirhossein was killed 💔", font_huge, RED, WIDTH//2, HEIGHT//2 - 50, center=True)
        draw_text("Amirhossein lost his life...", font_medium, WHITE, WIDTH//2, HEIGHT//2 + 40, center=True)
        
        if GameData.win_count >= 2 and not GameData.DOUBLE_JUMP_UNLOCKED:
            GameData.DOUBLE_JUMP_UNLOCKED = True
            GameData.MAX_JUMPS = 2
            GameData.save_progress()  # سیو خودکار بعد از آنلاک
        
        if GameData.DOUBLE_JUMP_UNLOCKED:
            draw_text("✅ Double Jump Unlocked! (Press Space twice in air)", font_small, GOLD, WIDTH//2, HEIGHT//2 + 80, center=True)
        else:
            draw_text(f"Win {GameData.win_count}/2 to unlock Double Jump", font_small, YELLOW, WIDTH//2, HEIGHT//2 + 80, center=True)
        
        draw_text("Press R to restart | S = Save", font_small, GRAY, WIDTH//2, HEIGHT - 50, center=True)
        dead_dino = Dino()
        dead_dino.x = WIDTH//2 - 50
        dead_dino.y = HEIGHT - 100
        dead_dino.draw(screen, dead=True)

# Main loop
dino = Dino()
cacti = []
birds = []
spawn_timer = 0
bird_timer = 0
running = True
save_message_timer = 0

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # سیو خودکار هنگام بستن بازی
            GameData.save_progress()
            running = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if state == "RUNNING":
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    dino.jump()
                if event.key == pygame.K_f:
                    FULLSCREEN = not FULLSCREEN
                    if FULLSCREEN:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))
                if event.key == pygame.K_s:
                    # سیو دستی با کلید S
                    if GameData.save_progress():
                        save_message_timer = 120  # 2 ثانیه نمایش پیام
            elif state == "CUTSCENE":
                if event.key == pygame.K_RETURN and cutscene_step < 3:
                    cutscene_step += 1
                if event.key == pygame.K_r and cutscene_step >= 3:
                    state = "RUNNING"
                    distance = 0
                    dino = Dino()
                    cacti.clear()
                    birds.clear()
                    spawn_timer = 0
                    bird_timer = 0
                    cutscene_step = 0
                    step_timer = 0
                    GameData.win_count += 1
                    if GameData.win_count >= 2:
                        GameData.DOUBLE_JUMP_UNLOCKED = True
                        GameData.MAX_JUMPS = 2
                        GameData.save_progress()
                if event.key == pygame.K_s:
                    # سیو دستی در کات‌سین
                    if GameData.save_progress():
                        save_message_timer = 120
            elif state == "GAMEOVER":
                if event.key == pygame.K_r:
                    state = "RUNNING"
                    distance = 0
                    dino = Dino()
                    cacti.clear()
                    birds.clear()
                    spawn_timer = 0
                    bird_timer = 0
                    cutscene_step = 0
                    step_timer = 0
                if event.key == pygame.K_s:
                    if GameData.save_progress():
                        save_message_timer = 120

    if state == "RUNNING":
        dino.update()

        spawn_timer += 1
        if spawn_timer > random.randint(70, 130):
            if len(cacti) == 0 or cacti[-1].x < WIDTH - 250:
                cacti.append(Cactus(WIDTH + 20))
            spawn_timer = 0

        bird_timer += 1
        if bird_timer > random.randint(150, 300):
            if len(birds) == 0 or birds[-1].x < WIDTH - 300:
                cactus_near = False
                for c in cacti:
                    if c.x > WIDTH - 200:
                        cactus_near = True
                        break
                if not cactus_near:
                    birds.append(Bird(WIDTH + 20))
            bird_timer = 0

        for cactus in cacti[:]:
            cactus.update()
            if cactus.x < -50:
                cacti.remove(cactus)
                continue
            if dino.get_rect().colliderect(cactus.get_rect()):
                state = "GAMEOVER"
                dino.dead = True

        for bird in birds[:]:
            bird.update()
            if bird.x < -50:
                birds.remove(bird)
                continue
            if dino.get_rect().colliderect(bird.get_rect()):
                state = "GAMEOVER"
                dino.dead = True

        distance += 0.7
        if distance >= TARGET_DISTANCE:
            state = "CUTSCENE"
            cutscene_step = 0
            step_timer = 0
            dino.dead = True

    if state == "CUTSCENE":
        step_timer += 1
        if step_timer > 180:
            step_timer = 0

    # نمایش پیام سیو
    if save_message_timer > 0:
        save_message_timer -= 1
        draw_text("✅ Game Saved!", font_medium, GOLD, WIDTH//2, 30, center=True)

    # Drawing
    if state == "RUNNING":
        draw_ground()
        pygame.draw.ellipse(screen, GRAY, (100, 50, 60, 30))
        pygame.draw.ellipse(screen, GRAY, (500, 80, 80, 30))
        for cactus in cacti:
            cactus.draw(screen)
        for bird in birds:
            bird.draw(screen)
        dino.draw(screen)
        draw_text(f"Distance: {int(distance)} / {TARGET_DISTANCE}", font_small, BLACK, 20, 20)
        draw_text("Space=Jump | F=Fullscreen | S=Save", font_small, GRAY, 20, HEIGHT - 50)
        if GameData.MAX_JUMPS == 2:
            draw_text("✅ Double Jump Active", font_small, GOLD, WIDTH - 200, 20)
        elif GameData.win_count >= 1:
            draw_text(f"Win {GameData.win_count}/2 for Double Jump", font_small, YELLOW, WIDTH - 250, 20)

    elif state == "GAMEOVER":
        draw_ground()
        for cactus in cacti:
            cactus.draw(screen)
        for bird in birds:
            bird.draw(screen)
        dino.draw(screen, dead=True)
        draw_text("💀 Amirhossein was killed 💀", font_huge, RED, WIDTH//2, HEIGHT//2 - 30, center=True)
        draw_text("Press R to Restart | S = Save", font_small, BLACK, 20, HEIGHT - 50)

    elif state == "CUTSCENE":
        draw_cutscene(cutscene_step, step_timer)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
