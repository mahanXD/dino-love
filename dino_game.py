import pygame
import random
import sys
import math
import json
import os

# ---------- راه‌اندازی ----------
pygame.init()
pygame.mixer.init()
pygame.font.init()  # ← این خط جدید

# ---------- پیدا کردن مسیر ----------
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else BASE_DIR

PIC_DIR = os.path.join(DATA_DIR, "pic")
SOUND_DIR = os.path.join(DATA_DIR, "sound")
SAVE_FILE = os.path.join(DATA_DIR, "save.json")

os.makedirs(PIC_DIR, exist_ok=True)
os.makedirs(SOUND_DIR, exist_ok=True)

# ---------- تنظیمات صفحه ----------
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Love - Amirhossein")
clock = pygame.time.Clock()

# ---------- فونت‌ها ----------
font_small = pygame.font.Font(None, 24)
font_medium = pygame.font.Font(None, 40)
font_large = pygame.font.Font(None, 60)
font_huge = pygame.font.Font(None, 80)

# ---------- رنگ‌ها ----------
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
LIGHT_GREEN = (50, 200, 50)

# ---------- متغیرهای اصلی ----------
state = "RUNNING"
distance = 0
FULLSCREEN = False
cutscene_step = 0
step_timer = 0

# ---------- سیستم Difficulty ----------
DIFFICULTY = "normal"

def get_difficulty_settings(difficulty):
    settings = {
        "easy": {
            "base_speed": 4,
            "max_speed": 8,
            "target_distance": 3000,
            "spawn_cactus_min": 90,
            "spawn_cactus_max": 150,
            "spawn_bird_min": 200,
            "spawn_bird_max": 350,
            "label": "Easy"
        },
        "normal": {
            "base_speed": 6,
            "max_speed": 11,
            "target_distance": 5000,
            "spawn_cactus_min": 70,
            "spawn_cactus_max": 130,
            "spawn_bird_min": 150,
            "spawn_bird_max": 300,
            "label": "Normal"
        },
        "hard": {
            "base_speed": 8,
            "max_speed": 14,
            "target_distance": 7000,
            "spawn_cactus_min": 50,
            "spawn_cactus_max": 100,
            "spawn_bird_min": 100,
            "spawn_bird_max": 250,
            "label": "Hard"
        },
        "impossible": {
            "base_speed": 10,
            "max_speed": 16,
            "target_distance": 10000,
            "spawn_cactus_min": 30,
            "spawn_cactus_max": 80,
            "spawn_bird_min": 70,
            "spawn_bird_max": 200,
            "label": "Impossible"
        }
    }
    return settings.get(difficulty, settings["normal"])

current_settings = get_difficulty_settings(DIFFICULTY)
BASE_SPEED = current_settings["base_speed"]
MAX_SPEED = current_settings["max_speed"]
TARGET_DISTANCE = current_settings["target_distance"]

# ---------- کلاس مدیریت Assets ----------
class AssetManager:
    images = {}
    sounds = {}

    @staticmethod
    def get_base_dir():
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def load_image(name):
        if name in AssetManager.images:
            return AssetManager.images[name]
        
        path_main = os.path.join(DATA_DIR, "pic", name + ".png")
        path_embedded = os.path.join(AssetManager.get_base_dir(), "pic", name + ".png")
        
        for path in [path_main, path_embedded]:
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    AssetManager.images[name] = img
                    return img
            except:
                pass
        
        AssetManager.images[name] = None
        return None

    @staticmethod
    def load_sound(name):
        if name in AssetManager.sounds:
            return AssetManager.sounds[name]
        
        extensions = [".wav", ".mp3", ".ogg", ".wav.mp3", ".mp3.wav"]
        
        for ext in extensions:
            path_main = os.path.join(DATA_DIR, "sound", name + ext)
            path_embedded = os.path.join(AssetManager.get_base_dir(), "sound", name + ext)
            
            for path in [path_main, path_embedded]:
                try:
                    if os.path.exists(path):
                        sound = pygame.mixer.Sound(path)
                        AssetManager.sounds[name] = sound
                        return sound
                except:
                    pass
        
        AssetManager.sounds[name] = None
        return None

# ---------- کلاس مدیریت ذخیره‌سازی ----------
class SaveManager:
    @staticmethod
    def save(win_count, max_jumps, double_jump_unlocked):
        data = {
            "win_count": win_count,
            "max_jumps": max_jumps,
            "double_jump_unlocked": double_jump_unlocked
        }
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f)
            return True
        except:
            return False

    @staticmethod
    def load():
        if not os.path.exists(SAVE_FILE):
            return None
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except:
            return None

# ---------- کلاس مدیریت داده‌های بازی ----------
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

GameData.load_from_save()

# ---------- بارگذاری صداها ----------
jump_sound = AssetManager.load_sound("jump")
die_sound = AssetManager.load_sound("die")
win_sound = AssetManager.load_sound("win")
cutscene1_sound = AssetManager.load_sound("cutscene1")
cutscene2_sound = AssetManager.load_sound("cutscene2")
cutscene3_sound = AssetManager.load_sound("cutscene3")

# ---------- محاسبه سرعت بر اساس مسافت ----------
def get_current_speed():
    if distance < 1000:
        return BASE_SPEED
    elif distance < 2000:
        return min(BASE_SPEED + 1, MAX_SPEED)
    elif distance < 3000:
        return min(BASE_SPEED + 2, MAX_SPEED)
    elif distance < 4000:
        return min(BASE_SPEED + 3, MAX_SPEED)
    else:
        return min(BASE_SPEED + 4, MAX_SPEED)

# ---------- کلاس دایناسور ----------
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

        self.img_normal = AssetManager.load_image("dino")
        self.img_sad = AssetManager.load_image("dino_sad")
        self.img_dead = AssetManager.load_image("dino_dead")
        self.img_bride = AssetManager.load_image("bride")
        self.img_groom = AssetManager.load_image("groom")

    def jump(self):
        if not self.dead and self.jumps_used < GameData.MAX_JUMPS:
            self.y_vel = -12
            self.jumping = True
            self.jumps_used += 1
            if jump_sound:
                jump_sound.play()

    def update(self):
        if self.dead:
            return
        self.y += self.y_vel
        self.y_vel += 0.7
        if self.y >= HEIGHT - 60:
            self.y = HEIGHT - 60
            self.y_vel = 0
            self.jumping = False
            self.jumps_used = 0

    def draw(self, screen, sad=False, dead=False):
        if dead and self.img_dead:
            img = self.img_dead
        elif sad and self.img_sad:
            img = self.img_sad
        elif self.img_normal:
            img = self.img_normal
        else:
            color = (50, 50, 50) if not dead else (80, 80, 80)
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, color, (self.x + self.width - 10, self.y - 15, 15, 15))
            if dead:
                pygame.draw.line(screen, BLACK, (self.x + self.width - 8, self.y - 8),
                                 (self.x + self.width - 2, self.y - 8), 2)
                pygame.draw.line(screen, color, (self.x + 5, self.y + self.height),
                                 (self.x - 5, self.y + self.height + 10), 5)
                pygame.draw.line(screen, color, (self.x + self.width - 5, self.y + self.height),
                                 (self.x + self.width + 5, self.y + self.height + 10), 5)
            else:
                if sad:
                    pygame.draw.circle(screen, WHITE, (self.x + self.width - 5, self.y - 10), 3)
                    pygame.draw.circle(screen, BLACK, (self.x + self.width - 3, self.y - 10), 1)
                    pygame.draw.line(screen, BLACK, (self.x + self.width - 10, self.y - 18),
                                     (self.x + self.width - 3, self.y - 18), 2)
                else:
                    pygame.draw.circle(screen, WHITE, (self.x + self.width - 5, self.y - 10), 3)
                    pygame.draw.circle(screen, BLACK, (self.x + self.width - 3, self.y - 10), 1)
                if not self.jumping:
                    pygame.draw.line(screen, color, (self.x + 5, self.y + self.height),
                                     (self.x + 10, self.y + self.height + 15), 5)
                    pygame.draw.line(screen, color, (self.x + self.width - 5, self.y + self.height),
                                     (self.x + self.width - 10, self.y + self.height + 15), 5)
            self._draw_double_jump_indicator(screen)
            return

        img = pygame.transform.scale(img, (self.width, self.height))
        screen.blit(img, (self.x, self.y))
        self._draw_double_jump_indicator(screen)

    def _draw_double_jump_indicator(self, screen):
        if GameData.MAX_JUMPS == 2 and not self.dead:
            remaining = GameData.MAX_JUMPS - self.jumps_used
            for i in range(remaining):
                pygame.draw.circle(screen, GOLD, (self.x - 10 - i * 12, self.y - 5), 4)

    def draw_with_clothes(self, screen, is_bride=False):
        if is_bride and self.img_bride:
            img = self.img_bride
        elif not is_bride and self.img_groom:
            img = self.img_groom
        else:
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
                pygame.draw.polygon(screen, RED, [(self.x + 10, self.y - 5),
                                                  (self.x + 15, self.y + 5),
                                                  (self.x + 20, self.y - 5)])
            return
        img = pygame.transform.scale(img, (self.width, self.height))
        screen.blit(img, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 5)

# ---------- کلاس کاکتوس ----------
class Cactus:
    def __init__(self, x):
        self.width = 20
        self.height = random.randint(35, 55)
        self.x = x
        self.y = HEIGHT - 20 - self.height
        self.img = AssetManager.load_image("cactus")

    def update(self, speed):
        self.x -= speed

    def draw(self, screen):
        if self.img:
            img = pygame.transform.scale(self.img, (self.width, self.height))
            screen.blit(img, (self.x, self.y))
        else:
            pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, GREEN, (self.x - 6, self.y + 10, 8, 8))
            pygame.draw.rect(screen, GREEN, (self.x + self.width - 2, self.y + 20, 8, 8))
            pygame.draw.rect(screen, GREEN, (self.x - 4, self.y + 30, 6, 6))

    def get_rect(self):
        return pygame.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 4)

# ---------- کلاس پرنده ----------
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
        self.img = AssetManager.load_image("bird")

    def update(self, speed):
        self.x -= speed
        self.timer += 1
        if self.timer > 8:
            self.wing_up = not self.wing_up
            self.timer = 0
        self.y = self.base_y + 3 * math.sin(self.wave_offset * 0.05)
        self.wave_offset += 1

    def draw(self, screen):
        if self.img:
            img = pygame.transform.scale(self.img, (self.width, self.height))
            screen.blit(img, (self.x, self.y))
        else:
            pygame.draw.ellipse(screen, BLUE, (self.x, self.y, self.width, self.height))
            if self.wing_up:
                pygame.draw.polygon(screen, BLUE, [(self.x + 5, self.y),
                                                   (self.x + 15, self.y - 15),
                                                   (self.x + 25, self.y)])
            else:
                pygame.draw.polygon(screen, BLUE, [(self.x + 5, self.y + self.height),
                                                   (self.x + 15, self.y + self.height + 15),
                                                   (self.x + 25, self.y + self.height)])
            pygame.draw.circle(screen, WHITE, (self.x + 25, self.y + 5), 3)
            pygame.draw.circle(screen, BLACK, (self.x + 26, self.y + 5), 1)

    def get_rect(self):
        return pygame.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 4)

# ---------- توابع رسم ----------
def draw_ground():
    ground_img = AssetManager.load_image("ground")
    if ground_img:
        ground_img = pygame.transform.scale(ground_img, (WIDTH, 20))
        screen.blit(ground_img, (0, HEIGHT - 20))
    else:
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

# ---------- کات‌سین ----------
def draw_cutscene(step, timer):
    screen.fill(LIGHT_GREEN)

    if step == 0:
        draw_text("Amirhossein started running after his love...", font_medium, BLACK, WIDTH//2, 50, center=True)
        dino = Dino()
        dino.x = 200
        dino.y = HEIGHT - 120
        dino.draw(screen)
        draw_ground()
        draw_text("Press ENTER to continue", font_small, GRAY, WIDTH//2, HEIGHT - 30, center=True)
        if cutscene1_sound:
            cutscene1_sound.play()

    elif step == 1:
        draw_text("Amirhossein arrived, but saw his love marrying someone else!", font_medium, BLACK, WIDTH//2, 30, center=True)
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
        draw_text("Press ENTER to continue", font_small, GRAY, WIDTH//2, HEIGHT - 30, center=True)
        if cutscene2_sound:
            cutscene2_sound.play()

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
        for _ in range(5):
            x = WIDTH // 2 + 80 + random.randint(-20, 20)
            y = HEIGHT // 2 + random.randint(-30, 30)
            pygame.draw.line(screen, YELLOW, (x, y), (x + 20, y - 20), 3)
        draw_ground()
        draw_text("Press ENTER to continue", font_small, GRAY, WIDTH//2, HEIGHT - 30, center=True)
        if cutscene3_sound:
            cutscene3_sound.play()

    elif step >= 3:
        screen.fill((30, 0, 0))
        draw_text("💔 Amirhossein was killed 💔", font_huge, RED, WIDTH//2, HEIGHT//2 - 50, center=True)
        draw_text("Amirhossein lost his life...", font_medium, WHITE, WIDTH//2, HEIGHT//2 + 40, center=True)

        if GameData.win_count >= 2 and not GameData.DOUBLE_JUMP_UNLOCKED:
            GameData.DOUBLE_JUMP_UNLOCKED = True
            GameData.MAX_JUMPS = 2
            GameData.save_progress()
            if win_sound:
                win_sound.play()

        if GameData.DOUBLE_JUMP_UNLOCKED:
            draw_text("✅ Double Jump Unlocked! (Press Space twice in air)", font_small, GOLD, WIDTH//2, HEIGHT//2 + 80, center=True)
        else:
            draw_text(f"Win {GameData.win_count}/2 to unlock Double Jump", font_small, YELLOW, WIDTH//2, HEIGHT//2 + 80, center=True)

        draw_text("Press R to restart | S = Save", font_small, GRAY, WIDTH//2, HEIGHT - 50, center=True)
        dead_dino = Dino()
        dead_dino.x = WIDTH // 2 - 50
        dead_dino.y = HEIGHT - 100
        dead_dino.draw(screen, dead=True)

# ---------- صفحه Game Over ----------
def draw_game_over_screen():
    screen.fill((30, 30, 30))
    
    draw_text("💀 Amirhossein was killed 💀", font_huge, RED, WIDTH//2, 100, center=True)
    draw_text("Choose Difficulty:", font_medium, WHITE, WIDTH//2, 170, center=True)
    
    difficulties = ["Easy", "Normal", "Hard", "Impossible"]
    colors = [GREEN, YELLOW, (255, 150, 0), RED]
    keys = ["1", "2", "3", "4"]
    
    for i, (diff, color) in enumerate(zip(difficulties, colors)):
        x = 150 + i * 140
        y = 230
        rect = pygame.Rect(x - 40, y - 20, 100, 50)
        pygame.draw.rect(screen, color, rect, 2)
        draw_text(f"{keys[i]}. {diff}", font_medium, color, x, y, center=True)
        
        if DIFFICULTY == diff.lower():
            pygame.draw.rect(screen, WHITE, rect, 1)
            draw_text("⬅", font_medium, WHITE, x - 55, y, center=True)
            draw_text("➡", font_medium, WHITE, x + 55, y, center=True)
    
    settings = get_difficulty_settings(DIFFICULTY)
    info_text = f"Speed: {settings['base_speed']}-{settings['max_speed']} | Distance: {settings['target_distance']} | Obstacles: {settings['spawn_cactus_min']}-{settings['spawn_cactus_max']}"
    draw_text(info_text, font_small, GRAY, WIDTH//2, 310, center=True)
    
    draw_text("Press 1-4 to select | R to restart with current", font_small, GRAY, WIDTH//2, HEIGHT - 50, center=True)

# ---------- تابع ریستارت ----------
def reset_game():
    global state, distance, dino, cacti, birds, spawn_timer, bird_timer, cutscene_step, step_timer
    state = "RUNNING"
    distance = 0
    dino = Dino()
    cacti.clear()
    birds.clear()
    spawn_timer = 0
    bird_timer = 0
    cutscene_step = 0
    step_timer = 0

# ---------- حلقه اصلی ----------
dino = Dino()
cacti = []
birds = []
spawn_timer = 0
bird_timer = 0
running = True
save_message_timer = 0

while running:
    screen.fill(WHITE)
    current_speed = get_current_speed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            GameData.save_progress()
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if state == "RUNNING":
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    dino.jump()
                if event.key == pygame.K_f:
                    FULLSCREEN = not FULLSCREEN
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if FULLSCREEN else (WIDTH, HEIGHT))
                if event.key == pygame.K_s:
                    if GameData.save_progress():
                        save_message_timer = 120

            elif state == "GAMEOVER":
                if event.key == pygame.K_1:
                    DIFFICULTY = "easy"
                    current_settings = get_difficulty_settings(DIFFICULTY)
                    BASE_SPEED = current_settings["base_speed"]
                    MAX_SPEED = current_settings["max_speed"]
                    TARGET_DISTANCE = current_settings["target_distance"]
                    reset_game()
                elif event.key == pygame.K_2:
                    DIFFICULTY = "normal"
                    current_settings = get_difficulty_settings(DIFFICULTY)
                    BASE_SPEED = current_settings["base_speed"]
                    MAX_SPEED = current_settings["max_speed"]
                    TARGET_DISTANCE = current_settings["target_distance"]
                    reset_game()
                elif event.key == pygame.K_3:
                    DIFFICULTY = "hard"
                    current_settings = get_difficulty_settings(DIFFICULTY)
                    BASE_SPEED = current_settings["base_speed"]
                    MAX_SPEED = current_settings["max_speed"]
                    TARGET_DISTANCE = current_settings["target_distance"]
                    reset_game()
                elif event.key == pygame.K_4:
                    DIFFICULTY = "impossible"
                    current_settings = get_difficulty_settings(DIFFICULTY)
                    BASE_SPEED = current_settings["base_speed"]
                    MAX_SPEED = current_settings["max_speed"]
                    TARGET_DISTANCE = current_settings["target_distance"]
                    reset_game()
                elif event.key == pygame.K_r:
                    reset_game()

            elif state == "CUTSCENE":
                if event.key == pygame.K_RETURN and cutscene_step < 3:
                    cutscene_step += 1
                if event.key == pygame.K_r and cutscene_step >= 3:
                    reset_game()
                    GameData.win_count += 1
                    if GameData.win_count >= 2:
                        GameData.DOUBLE_JUMP_UNLOCKED = True
                        GameData.MAX_JUMPS = 2
                        GameData.save_progress()
                if event.key == pygame.K_s:
                    if GameData.save_progress():
                        save_message_timer = 120

    if state == "RUNNING":
        dino.update()

        spawn_timer += 1
        c_min = current_settings["spawn_cactus_min"]
        c_max = current_settings["spawn_cactus_max"]
        if spawn_timer > random.randint(c_min, c_max):
            if not cacti or cacti[-1].x < WIDTH - 250:
                cacti.append(Cactus(WIDTH + 20))
            spawn_timer = 0

        bird_timer += 1
        b_min = current_settings["spawn_bird_min"]
        b_max = current_settings["spawn_bird_max"]
        if bird_timer > random.randint(b_min, b_max):
            if not birds or birds[-1].x < WIDTH - 300:
                cactus_near = any(c.x > WIDTH - 200 for c in cacti)
                if not cactus_near:
                    birds.append(Bird(WIDTH + 20))
            bird_timer = 0

        for cactus in cacti[:]:
            cactus.update(current_speed)
            if cactus.x < -50:
                cacti.remove(cactus)
            elif dino.get_rect().colliderect(cactus.get_rect()):
                state = "GAMEOVER"
                dino.dead = True
                if die_sound:
                    die_sound.play()

        for bird in birds[:]:
            bird.update(current_speed)
            if bird.x < -50:
                birds.remove(bird)
            elif dino.get_rect().colliderect(bird.get_rect()):
                state = "GAMEOVER"
                dino.dead = True
                if die_sound:
                    die_sound.play()

        distance += 0.7
        if distance >= TARGET_DISTANCE:
            state = "CUTSCENE"
            cutscene_step = 0
            step_timer = 0
            dino.dead = True
            if win_sound:
                win_sound.play()

    if state == "CUTSCENE":
        step_timer += 1
        if step_timer > 180:
            step_timer = 0

    if save_message_timer > 0:
        save_message_timer -= 1
        draw_text("✅ Game Saved!", font_medium, GOLD, WIDTH//2, 30, center=True)

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
        draw_text(f"Speed: {current_speed} | {current_settings['label']}", font_small, BLACK, 20, 45)
        draw_text("Space=Jump | F=Fullscreen | S=Save", font_small, GRAY, 20, HEIGHT - 50)

        if GameData.MAX_JUMPS == 2:
            draw_text("✅ Double Jump Active", font_small, GOLD, WIDTH - 200, 20)
        elif GameData.win_count >= 1:
            draw_text(f"Win {GameData.win_count}/2 for Double Jump", font_small, YELLOW, WIDTH - 250, 20)

    elif state == "GAMEOVER":
        draw_game_over_screen()

    elif state == "CUTSCENE":
        draw_cutscene(cutscene_step, step_timer)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()