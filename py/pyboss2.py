import json
from pathlib import Path
import math
import random
import pygame

pygame.init()

# =========================
# 기본 설정 - 1920 x 1080 UI
# =========================
W, H = 1920, 1080
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("SOUL JUMP - TUTORIAL & BOSS RUSH")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("malgungothic", 34)
BIG = pygame.font.SysFont("malgungothic", 54, bold=True)
SMALL = pygame.font.SysFont("malgungothic", 26)
LOGIC_FONT = pygame.font.SysFont("malgungothic", 22, bold=True)
SMALL_FONT = pygame.font.SysFont("malgungothic", 18)
WORD_FONT = pygame.font.SysFont("arial", 42, bold=True)
WORD_BULLET_FONT = pygame.font.SysFont("arial", 26, bold=True)

BLACK = (10, 8, 20)
WHITE = (245, 245, 255)
RED = (255, 65, 95)
CYAN = (80, 230, 255)
PURPLE = (175, 90, 255)
YELLOW = (255, 220, 80)
ORANGE = (255, 150, 55)
GREEN = (100, 255, 150)
PINK = (255, 100, 190)

ARENA = pygame.Rect(310, 240, 1300, 700)

# =========================
# 랭킹 파일 연동 설정
# =========================
LEADERBOARD_FILE = Path(__file__).with_name("soul_jump_ranking.json")
try:
    loaded = json.loads(LEADERBOARD_FILE.read_text(encoding="utf-8"))
    leaderboard = loaded if isinstance(loaded, list) else []
except (FileNotFoundError, json.JSONDecodeError, OSError):
    leaderboard = []
leaderboard = [row for row in leaderboard if isinstance(row, dict)]

def save_leaderboard():
    try:
        LEADERBOARD_FILE.write_text(json.dumps(leaderboard, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass

# =========================
# 데이터 정의
# =========================
ENGLISH_WORDS = [
    ("ambiguous", "모호한"), ("benevolent", "자비로운"), ("candid", "솔직한"),
    ("deteriorate", "악화되다"), ("eloquent", "웅변을 잘하는"), ("feasible", "실현 가능한"),
    ("gullible", "잘 속는"), ("hypothesis", "가설"), ("inevitable", "피할 수 없는"),
    ("meticulous", "꼼꼼한"), ("nostalgia", "향수"), ("pragmatic", "실용적인"),
    ("resilient", "회복력 있는"), ("skeptical", "회의적인"), ("ubiquitous", "어디에나 있는"),
    ("apple", "사과"), ("banana", "바나나"), ("school", "학교"), ("friend", "친구"),
    ("happy", "행복한"), ("water", "물"), ("house", "집"), ("book", "책"),
    ("music", "음악"), ("flower", "꽃"), ("sun", "태양"), ("moon", "달"),
    ("teacher", "선생님"), ("family", "가족"), ("animal", "동물"),
]

LOGIC_FORMS = [
    ("보스가 파란색이라면 공격한다"),
    ("보스가 빨간색이라면 공격한다"),
    ("보스가 파란색이 아니라면 공격한다"),
    ("보스가 빨간색이 아니라면 공격한다"),
    ("보스가 파란색이라면 공격하지 않는다"),
    ("보스가 빨간색이라면 공격하지 않는다"),
]

# =========================
# 플레이어 클래스
# =========================
class Player:
    def __init__(self):
        self.x = ARENA.centerx
        self.y = ARENA.bottom - 70
        self.r = 14
        self.hp = 5
        self.jump = 0
        self.jump_time = 0
        self.jump_cooldown = 0
        self.invincible = 0
        self.shoot_cooldown = 0

    def update(self, keys):
        speed = 7
        dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])

        if dx != 0 and dy != 0:
            speed_factor = 1 / math.sqrt(2)
        else:
            speed_factor = 1

        self.x += dx * speed * speed_factor
        self.y += dy * speed * speed_factor

        self.x = max(ARENA.left + 20, min(ARENA.right - 20, self.x))
        self.y = max(ARENA.top + 20, min(ARENA.bottom - 20, self.y))

        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.jump_time > 0:
            self.jump_time -= 1
            t = 1 - self.jump_time / 32
            self.jump = math.sin(t * math.pi) * 60
        else:
            self.jump = 0

    def do_jump(self):
        if self.jump_cooldown <= 0 and self.jump_time <= 0:
            self.jump_time = 32
            self.jump_cooldown = 48

    def draw(self):
        pygame.draw.ellipse(screen, (65, 55, 80), (self.x - 18, self.y - 7, 36, 14))
        draw_y = int(self.y - self.jump)

        points = [
            (self.x, draw_y - 20), (self.x + 18, draw_y - 4),
            (self.x + 13, draw_y + 13), (self.x, draw_y + 20),
            (self.x - 13, draw_y + 13), (self.x - 18, draw_y - 4),
        ]
        body_color = CYAN if self.jump_time > 0 else RED
        pygame.draw.polygon(screen, body_color, points)
        pygame.draw.circle(screen, WHITE, (int(self.x - 5), int(draw_y - 2)), 4)
        pygame.draw.circle(screen, WHITE, (int(self.x + 5), int(draw_y - 2)), 4)


# =========================
# 탄환 및 투사체 클래스
# =========================
class Bullet:
    def __init__(self, x, y, vx, vy, color, radius=9, ground=False, life=360, ax=0, ay=0):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx * 1.2
        self.vy = vy * 1.2
        self.ax = ax * 1.2
        self.ay = ay * 1.2
        self.color = color
        self.r = radius
        self.ground = ground
        self.life = life

    def update(self):
        self.vx += self.ax
        self.vy += self.ay
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(screen, WHITE, (int(self.x - 2), int(self.y - 2)), max(1, self.r // 3))

    def alive(self):
        return self.life > 0 and -50 < self.x < W + 50 and -60 < self.y < H + 60


class WordBullet(Bullet):
    def __init__(self, x, y, vx, vy, word, color):
        super().__init__(x, y, vx, vy, color, radius=11, ground=False, life=300)
        self.word = word

    def draw(self):
        image = WORD_BULLET_FONT.render(self.word, True, self.color)
        rect = image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(image, rect)


class GiantWaveBullet:
    def __init__(self, start_x, freq_offset=0):
        self.x = float(start_x)
        self.start_y = float(ARENA.centery)
        self.vx = 3.0
        self.r = 90
        self.color = CYAN
        self.freq = 0.03
        self.amp = 220
        self.elapsed = freq_offset
        self.active = True

    def update(self):
        if not self.active: return
        self.elapsed += 1
        self.x += self.vx
        self.y = self.start_y + math.sin(self.elapsed * self.freq) * self.amp
        if self.x > ARENA.right - 90: self.vx = -3.0
        elif self.x < ARENA.left + 90: self.vx = 3.0

    def draw(self):
        if not self.active: return
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(screen, WHITE, (int(self.x - 12), int(self.y - 12)), max(6, self.r // 3))


class FactorBullet:
    def __init__(self, x, y, vx, vy):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.r = 14
        self.color = GREEN
        self.life = 250
        self.split_timer = 65

    def update(self, bullets_list, boss_dialogue_ref, speed_mult):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.split_timer -= 1
        if self.split_timer <= 0:
            boss_dialogue_ref[0] = "인수분해!"
            boss_dialogue_ref[1] = 45
            base_angle = math.atan2(self.vy, self.vx)
            for spread in [-0.3, 0.0, 0.3]:
                angle = base_angle + spread
                speed = 4.0 * speed_mult
                bullets_list.append(Bullet(self.x, self.y, math.cos(angle) * speed, math.sin(angle) * speed, GREEN, radius=8, life=200))
            return True
        return False

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(screen, WHITE, (int(self.x - 3), int(self.y - 3)), 4)


class CirclePatternHazard:
    def __init__(self, x=None, y=None):
        if x is not None and y is not None:
            self.x = x
            self.y = y
        else:
            self.x = random.randint(ARENA.left + 120, ARENA.right - 120)
            self.y = random.randint(ARENA.top + 120, ARENA.bottom - 120)
        self.r = 100
        self.timer = 60
        self.exploded = False

    def update(self, bullets_list, speed_mult):
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                self.explode(bullets_list, speed_mult)

    def explode(self, bullets_list, speed_mult):
        num_bullets = 12
        speed = 3.5 * speed_mult
        for i in range(num_bullets):
            angle = (i / num_bullets) * (2 * math.pi)
            bullets_list.append(Bullet(self.x, self.y, math.cos(angle) * speed, math.sin(angle) * speed, PURPLE, radius=8, life=250))
        self.exploded = True

    def draw(self):
        if not self.exploded:
            alpha_color = (255, 100, 255) if (self.timer // 10) % 2 == 0 else (150, 50, 150)
            pygame.draw.circle(screen, alpha_color, (int(self.x), int(self.y)), self.r, 3)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 4)


class Shot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = -12
        self.r = 7

    def update(self):
        self.y += self.vy

    def draw(self):
        pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 3)


# =========================
# 화면 및 게임 상태 관리
# =========================
screen_mode = "input"  # input -> tutorial -> playing -> stage1_clear -> stage2_ready -> ranking
active_input = "name"
player_name = ""
student_id = ""

input_box_width = 420
input_box_height = 55
name_box_rect = pygame.Rect((W - input_box_width) // 2, 380, input_box_width, input_box_height)
id_box_rect = pygame.Rect((W - input_box_width) // 2, 510, input_box_width, input_box_height)
start_button_rect = pygame.Rect((W - 420) // 2, 630, 420, 60)
restart_button = pygame.Rect((W - 420) // 2, 920, 420, 55)

# 게임 객체 및 변수
player = Player()
bullets = []
shots = []
factor_bullets = []
circle_hazards = []
giant_bullet = GiantWaveBullet(ARENA.left + 90, 0)

stage = 1
boss_hp = 200
boss_max_hp = 200
boss_name = "영어 마스터 (CHAOS)"
boss_color = (255, 190, 70)
pattern_timer_1 = 0
pattern_timer_2 = 0
passive_shoot_timer = 0
current_pattern_name = "VOCABULARY TEST"
PATTERN_COUNT = 12

quiz_active = False
quiz_timer = 0
quiz_cooldown = 600
quiz_feedback = ""
quiz_feedback_timer = 0
quiz_word = None
quiz_choices = []
quiz_answer = 0

math_boss_hp = 300
math_boss_max_hp = 300
boss_dialogue = ["", 0]
boss_shoot_timer = 0
circle_spawn_timer = 0
factor_spawn_timer = 0
final_exam_active = False
final_exam_step = 0
final_exam_timer = 180
target_quadrant = 1
exam_phase = "waiting"

logic_round_active = False
logic_form_index = 0
logic_boss_blue = True
logic_should_attack = True
logic_feedback = ""
logic_feedback_timer = 0
logic_timer = 300
logic_failed_state = False

score_recorded = False


def init_game():
    global player, bullets, shots, factor_bullets, circle_hazards, giant_bullet
    global stage, boss_hp, math_boss_hp, frame, pattern_timer_1, pattern_timer_2, passive_shoot_timer
    global quiz_active, quiz_timer, quiz_cooldown, quiz_feedback, quiz_feedback_timer
    global final_exam_active, logic_round_active, logic_failed_state, score_recorded

    player = Player()
    bullets.clear()
    shots.clear()
    factor_bullets.clear()
    circle_hazards.clear()
    giant_bullet = GiantWaveBullet(ARENA.left + 90, 0)

    stage = 1
    boss_hp = 200
    math_boss_hp = 300
    frame = 0
    pattern_timer_1 = 0
    pattern_timer_2 = 0
    passive_shoot_timer = 0
    quiz_active = False
    quiz_timer = 0
    quiz_cooldown = 600
    quiz_feedback = ""
    quiz_feedback_timer = 0
    final_exam_active = False
    logic_round_active = False
    logic_failed_state = False
    score_recorded = False


def record_result(status, final_stage, b_hp_left, p_hp_left):
    global score_recorded
    if score_recorded: return
    score_recorded = True

    english_cleared = 200 if (final_stage > 1 or status == "Clear") else (200 - b_hp_left)
    math_cleared = (300 - b_hp_left) if final_stage == 2 else 0
    if status == "Clear": math_cleared = 300

    score = english_cleared + math_cleared
    if status == "Clear": detail = f"올클리어 (잔여 HP: {p_hp_left})"
    elif final_stage == 2: detail = f"수학 보스 도전 중 패배 (잡은 체력: {english_cleared + (300 - b_hp_left)})"
    else: detail = f"영어 보스 도전 중 패배 (잡은 체력: {english_cleared})"

    record = {
        "name": player_name.strip(),
        "student_id": student_id.strip(),
        "stage": final_stage,
        "status": status,
        "boss_hp_left": b_hp_left,
        "player_hp_left": p_hp_left,
        "score": score,
        "detail": detail
    }

    existing = next((r for r in leaderboard if r.get("student_id") == student_id and r.get("name") == player_name), None)
    if existing:
        if score > existing.get("score", 0):
            leaderboard.remove(existing)
            leaderboard.append(record)
    else:
        leaderboard.append(record)
    save_leaderboard()


def add_bullet(x, y, angle, speed, color, radius=9, ground=False, ax=0, ay=0):
    vx = math.cos(angle) * speed
    vy = math.sin(angle) * speed
    bullets.append(Bullet(x, y, vx, vy, color, radius, ground, 360, ax, ay))

def aim_angle(x1, y1, x2, y2):
    return math.atan2(y2 - y1, x2 - x1)

def add_word_bullet(x, y, angle, speed, word=None, color=None):
    if word is None: word = random.choice(ENGLISH_WORDS)[0]
    if color is None: color = random.choice([CYAN, PURPLE, PINK, ORANGE])
    bullets.append(WordBullet(x, y, math.cos(angle) * speed, math.sin(angle) * speed, word, color))


def spawn_random_pattern():
    global current_pattern_name
    p = random.randint(0, PATTERN_COUNT - 1)
    left, right = ARENA.left + 15, ARENA.right - 15
    top, bottom = ARENA.top + 15, ARENA.bottom - 15
    bx, by = ARENA.centerx, ARENA.top - 60

    if p == 0:
        current_pattern_name = "ALPHABET RAIN"
        for _ in range(20): add_bullet(random.randint(left, right), random.randint(top - 120, top), math.pi / 2, random.uniform(3.0, 4.5), CYAN, radius=8)
    elif p == 1:
        current_pattern_name = "GRAMMAR CROSS"
        for i in range(8):
            y = top + i * 75
            if y < bottom:
                add_bullet(left, y, 0, 3.5, YELLOW, radius=9)
                add_bullet(right, y, math.pi, 3.5, PURPLE, radius=9)
    elif p == 2:
        current_pattern_name = "ASGORE LETTER RING"
        for ring in range(6):
            base_angle = math.pi / 2 + ring * math.tau / 6
            offset = math.pi / 18 if ring % 2 else 0
            for j in range(4):
                add_word_bullet(bx, by, base_angle + offset + (j - 1.5) * 0.12, 3.0 + (j % 2) * 0.4, random.choice(["A", "E", "R", "S", "T", "O", "N"]), ORANGE if ring % 2 == 0 else PINK)
    elif p == 3:
        current_pattern_name = "PUNCTUATION STORM"
        for i in range(7):
            x = left + i * (right - left) / 6
            add_bullet(x, top, math.pi / 2 + 0.15, 4.0, RED, radius=9)
            add_bullet(right - (x - left), bottom, -math.pi / 2 - 0.15, 4.0, GREEN, radius=9)
    elif p == 4:
        current_pattern_name = "SENTENCE WAVE"
        for i in range(11):
            y = top + i * 55
            if y > bottom: break
            direction = 1 if i % 2 == 0 else -1
            bullets.append(Bullet(left if direction == 1 else right, y, direction * 3.0, 0, CYAN if direction == 1 else PURPLE, radius=8, ay=math.sin(i) * 0.035))
    elif p == 5:
        current_pattern_name = "WISDOM SOUL"
        for i in range(4):
            spread = (i - 1.5) * 0.14
            add_word_bullet(ARENA.left + 35, ARENA.centery, aim_angle(ARENA.left + 35, ARENA.centery, player.x, player.y) + spread, 3.2, color=PURPLE)
            add_word_bullet(ARENA.right - 35, ARENA.centery, aim_angle(ARENA.right - 35, ARENA.centery, player.x, player.y) - spread, 3.2, color=CYAN)
    elif p == 6:
        current_pattern_name = "FLOWER SPIRAL"
        cx, cy = ARENA.centerx, ARENA.top + 100
        rotation = frame * 0.018
        for petal in range(7):
            base_angle = math.tau * petal / 7 + rotation
            for j in range(3): add_bullet(cx, cy, base_angle + (j - 1) * 0.10, 2.5 + j * 0.35, GREEN if petal % 2 == 0 else PINK, radius=8)
    elif p == 7:
        current_pattern_name = "FINAL EXAM"
        for i in range(9):
            x = left + i * (right - left) / 8
            direction = 1 if i % 2 == 0 else -1
            bullets.append(Bullet(x, top, direction * 1.1, 3.2, ORANGE, radius=9, ax=-direction * 0.025))
            bullets.append(Bullet(x, bottom, -direction * 1.1, -3.2, CYAN, radius=9, ax=direction * 0.025))
    elif p == 8:
        current_pattern_name = "FAN SHOT"
        center_angle = aim_angle(bx, by, player.x, player.y)
        for i in range(9): add_bullet(bx, by, center_angle - math.radians(29) + math.radians(58) * i / 8, 3.4, ORANGE, radius=9)
    elif p == 9:
        current_pattern_name = "ZIGZAG DANCE"
        for i in range(8):
            y = top + i * 70
            if y > bottom: break
            direction = 1 if i % 2 == 0 else -1
            bullets.append(Bullet(left if direction == 1 else right, y, direction * 3.5, 0, PINK if direction == 1 else CYAN, radius=9, ay=0.045 if i % 2 == 0 else -0.045))
    elif p == 10:
        current_pattern_name = "ROTATING CROSS"
        for i in range(8): add_bullet(ARENA.centerx, ARENA.top + 100, math.tau * i / 8 + frame * 0.045, 3.0, PURPLE if i % 2 == 0 else CYAN, radius=9)
    else:
        current_pattern_name = "DOUBLE ARC"
        for i in range(6):
            y = ARENA.top + 60 + i * 100
            bullets.append(Bullet(left, y, 3.0, -0.15 + i * 0.045, YELLOW, radius=9, ay=0.025))
            bullets.append(Bullet(right, y, -3.0, 0.15 - i * 0.045, GREEN, radius=9, ay=-0.025))


def start_english_quiz():
    global quiz_active, quiz_timer, quiz_word, quiz_choices, quiz_answer
    bullets.clear()
    quiz_word = random.choice(ENGLISH_WORDS)
    correct_meaning = quiz_word[1]
    wrong_meanings = [meaning for word, meaning in ENGLISH_WORDS if meaning != correct_meaning]
    choices = random.sample(wrong_meanings, 3)
    choices.append(correct_meaning)
    random.shuffle(choices)
    quiz_choices = choices
    quiz_answer = choices.index(correct_meaning)
    quiz_active = True
    quiz_timer = 300

def finish_english_quiz(correct):
    global quiz_active, quiz_cooldown, quiz_feedback, quiz_feedback_timer, screen_mode
    if not quiz_active: return
    quiz_active = False
    quiz_cooldown = 600
    quiz_feedback_timer = 90
    if correct:
        quiz_feedback = "정답! (보스 데미지 없음)"
    else:
        quiz_feedback = "오답! HP -1"
        if player.invincible <= 0 and player.jump_time <= 0:
            player.hp -= 1
            player.invincible = 75
            if player.hp <= 0:
                record_result("Lose", 1, boss_hp, 0)
                screen_mode = "ranking"
                pygame.key.start_text_input()


def start_logic_round():
    global logic_round_active, logic_form_index, logic_boss_blue, logic_should_attack, logic_feedback, logic_timer
    logic_form_index = random.randrange(len(LOGIC_FORMS))
    logic_boss_blue = random.choice([True, False])
    statement = LOGIC_FORMS[logic_form_index]

    if "파란색이라면" in statement and "공격하지 않는다" not in statement:
        condition_true = logic_boss_blue
    elif "빨간색이라면" in statement and "공격하지 않는다" not in statement:
        condition_true = not logic_boss_blue
    elif "파란색이 아니라면" in statement:
        condition_true = not logic_boss_blue
    else:
        condition_true = logic_boss_blue

    if "공격하지 않는다" in statement:
        logic_should_attack = not logic_boss_blue if "파란색이라면" in statement else logic_boss_blue
    else:
        logic_should_attack = condition_true

    logic_round_active = True
    logic_timer = 300
    logic_feedback = ""

def finish_logic_round(correct, message):
    global logic_feedback, logic_feedback_timer, logic_failed_state
    logic_feedback = message if correct else "오답! 보스 체력 회복 모드"
    logic_feedback_timer = 120
    logic_failed_state = not correct


def draw_text(text, x, y, color=WHITE, font=FONT):
    image = font.render(str(text), True, color)
    screen.blit(image, (int(x), int(y)))

def draw_centered_text(text, rect, color=WHITE, font=FONT):
    image = font.render(str(text), True, color)
    screen.blit(image, image.get_rect(center=rect.center))

def draw_background_stars():
    for i in range(50):
        x = (i * 173 + 41) % W
        y = (i * 97 + 29) % H
        pygame.draw.circle(screen, (45, 40, 70), (x, y), 1)


# =========================
# 화면 그리기 함수들
# =========================
def draw_input_screen():
    screen.fill(BLACK)
    draw_background_stars()

    title_image = BIG.render("SOUL JUMP - BOSS RUSH", True, CYAN)
    screen.blit(title_image, title_image.get_rect(center=(W // 2, 200)))

    draw_text("참가자 이름", name_box_rect.x, name_box_rect.y - 35, YELLOW if active_input == "name" else WHITE, SMALL)
    pygame.draw.rect(screen, YELLOW if active_input == "name" else (100, 100, 120), name_box_rect, 2, border_radius=10)
    draw_text(player_name if player_name else "이름을 입력하세요...", name_box_rect.x + 15, name_box_rect.y + 12, WHITE if player_name else (130, 130, 145), SMALL)

    draw_text("학번", id_box_rect.x, id_box_rect.y - 35, YELLOW if active_input == "student_id" else WHITE, SMALL)
    pygame.draw.rect(screen, YELLOW if active_input == "student_id" else (100, 100, 120), id_box_rect, 2, border_radius=10)
    draw_text(student_id if student_id else "학번을 입력하세요...", id_box_rect.x + 15, id_box_rect.y + 12, WHITE if student_id else (130, 130, 145), SMALL)

    pygame.draw.rect(screen, (35, 30, 65), start_button_rect, border_radius=12)
    pygame.draw.rect(screen, CYAN, start_button_rect, 2, border_radius=12)
    draw_centered_text("게임 시작 (ENTER)", start_button_rect, YELLOW, FONT)
    draw_centered_text("TAB 또는 마우스로 입력칸 전환 | ESC: 종료", pygame.Rect(0, 720, W, 30), (165, 165, 190), SMALL_FONT)


def draw_tutorial_screen():
    screen.fill(BLACK)
    draw_background_stars()

    # 튜토리얼 안내 패널
    panel = pygame.Rect(W // 2 - 500, 120, 1000, 700)
    pygame.draw.rect(screen, (25, 22, 42), panel, border_radius=20)
    pygame.draw.rect(screen, CYAN, panel, 3, border_radius=20)

    title = BIG.render("🎮 튜토리얼 & 조작 설명", True, YELLOW)
    screen.blit(title, title.get_rect(center=(W // 2, 190)))

    # 애니메이션 예시 캐릭터 움직임 (좌우로 둥실둥실 이동)
    anim_x = W // 2 + int(math.sin(frame * 0.08) * 120)
    anim_y = 330 + int(abs(math.cos(frame * 0.1) * 20))
    pygame.draw.ellipse(screen, (65, 55, 80), (anim_x - 18, anim_y + 15, 36, 14))
    points = [
        (anim_x, anim_y - 20), (anim_x + 18, anim_y - 4),
        (anim_x + 13, anim_y + 13), (anim_x, anim_y + 20),
        (anim_x - 13, anim_y + 13), (anim_x - 18, anim_y - 4),
    ]
    pygame.draw.polygon(screen, RED, points)
    pygame.draw.circle(screen, WHITE, (anim_x - 5, anim_y - 2), 4)
    pygame.draw.circle(screen, WHITE, (anim_x + 5, anim_y - 2), 4)

    rules = [
        "1. [이동] : W, A, S, D 또는 방향키로 자유롭게 이동하세요.",
        "2. [점프] : SPACE 바를 누르면 점프하며, **점프 중에는 무적**이 됩니다!",
        "3. [공격] : U 또는 Z 키를 눌러 보스를 공격하세요.",
        "4. [퀴즈] : 화면에 나오는 퀴즈의 정답을 1~4 숫자키로 맞히세요.",
    ]

    y_pos = 420
    for r_text in rules:
        draw_centered_text(r_text, pygame.Rect(W // 2 - 450, y_pos, 900, 40), WHITE, FONT)
        y_pos += 65

    # 시작 버튼
    btn_rect = pygame.Rect(W // 2 - 250, 715, 500, 60)
    pygame.draw.rect(screen, (35, 30, 65), btn_rect, border_radius=12)
    pygame.draw.rect(screen, GREEN, btn_rect, 2, border_radius=12)
    draw_centered_text("ENTER를 눌러 보스전 시작하기!", btn_rect, GREEN, FONT)


def draw_ranking_screen():
    screen.fill(BLACK)
    draw_background_stars()

    title = BIG.render("SOUL JUMP - 명예의 전당 (RANKING)", True, CYAN)
    screen.blit(title, title.get_rect(center=(W // 2, 60)))

    panel = pygame.Rect(260, 135, 1400, 745)
    pygame.draw.rect(screen, (25, 22, 42), panel, border_radius=16)
    pygame.draw.rect(screen, PURPLE, panel, 2, border_radius=16)

    draw_text("순위", 300, 160, CYAN, FONT)
    draw_text("학번", 440, 160, CYAN, FONT)
    draw_text("이름", 680, 160, CYAN, FONT)
    draw_text("달성 단계 & 기록", 950, 160, CYAN, FONT)
    draw_text("점수 (잡은 체력)", 1400, 160, CYAN, FONT)
    pygame.draw.line(screen, (90, 85, 125), (290, 210), (1630, 210), 1)

    ranked = sorted(leaderboard, key=lambda row: int(row.get("score", 0) or 0), reverse=True)
    if not ranked:
        draw_centered_text("아직 저장된 점수 기록이 없습니다.", pygame.Rect(260, 450, 1400, 50), WHITE, FONT)
    else:
        for rank, row in enumerate(ranked[:12], start=1):
            y = 230 + (rank - 1) * 50
            sid = str(row.get("student_id", "-"))
            name = str(row.get("name", "알 수 없음"))
            detail = str(row.get("detail", ""))
            score = int(row.get("score", 0) or 0)
            highlight = sid == student_id and name == player_name
            color = YELLOW if highlight else WHITE

            draw_text(f"{rank:>2}.", 300, y, color, SMALL)
            draw_text(sid, 440, y, color, SMALL)
            draw_text(name, 680, y, color, SMALL)
            draw_text(detail, 950, y, color, SMALL)
            draw_text(f"{score:,}점", 1400, y, color, SMALL)

    pygame.draw.rect(screen, (35, 30, 65), restart_button, border_radius=12)
    pygame.draw.rect(screen, CYAN, restart_button, 2, border_radius=12)
    draw_centered_text("다시 하기 (ENTER)", restart_button, YELLOW, FONT)
    draw_centered_text("ESC: 종료", pygame.Rect(0, 990, W, 30), (165, 165, 190), SMALL_FONT)


def draw_arena():
    screen.fill(BLACK)
    for i in range(75):
        x = (i * 173 + 41) % W
        y = (i * 97 + 29) % H
        pygame.draw.circle(screen, (45, 40, 70), (x, y), 1)

    pygame.draw.rect(screen, (20, 15, 35), ARENA)
    for gx in range(ARENA.left + 50, ARENA.right, 50):
        pygame.draw.line(screen, (32, 35, 65), (gx, ARENA.top), (gx, ARENA.bottom), 1)
    for gy in range(ARENA.top + 50, ARENA.bottom, 50):
        pygame.draw.line(screen, (32, 35, 65), (ARENA.left, gy), (ARENA.right, gy), 1)

    if stage == 2 and final_exam_active:
        q_rects = {
            1: pygame.Rect(ARENA.centerx, ARENA.top, ARENA.width // 2, ARENA.height // 2),
            2: pygame.Rect(ARENA.left, ARENA.top, ARENA.width // 2, ARENA.height // 2),
            3: pygame.Rect(ARENA.left, ARENA.centery, ARENA.width // 2, ARENA.height // 2),
            4: pygame.Rect(ARENA.centerx, ARENA.centery, ARENA.width // 2, ARENA.height // 2),
        }
        if exam_phase == "checking":
            overlay = pygame.Surface((ARENA.width, ARENA.height), pygame.SRCALPHA)
            for q_num, q_rect in q_rects.items():
                if q_num != target_quadrant:
                    rel_rect = pygame.Rect(q_rect.x - ARENA.left, q_rect.y - ARENA.top, q_rect.width, q_rect.height)
                    pygame.draw.rect(overlay, (255, 60, 60, 110), rel_rect)
            screen.blit(overlay, ARENA.topleft)

        pygame.draw.line(screen, (200, 200, 255), (ARENA.centerx, ARENA.top), (ARENA.centerx, ARENA.bottom), 3)
        pygame.draw.line(screen, (200, 200, 255), (ARENA.left, ARENA.centery), (ARENA.right, ARENA.centery), 3)
        draw_text("제2사분면", ARENA.left + 50, ARENA.top + 30, (180, 180, 220), SMALL_FONT)
        draw_text("제1사분면", ARENA.right - 140, ARENA.top + 30, (180, 180, 220), SMALL_FONT)
        draw_text("제3사분면", ARENA.left + 50, ARENA.bottom - 50, (180, 180, 220), SMALL_FONT)
        draw_text("제4사분면", ARENA.right - 140, ARENA.bottom - 50, (180, 180, 220), SMALL_FONT)

    pygame.draw.rect(screen, WHITE, ARENA, 4)

    pulse = math.sin(frame * 0.06) * 6
    bx, by = ARENA.centerx, ARENA.top - 60

    if stage == 1:
        pygame.draw.circle(screen, boss_color, (bx, by), int(35 + pulse))
        pygame.draw.circle(screen, WHITE, (bx - 12, by - 5), 8)
        pygame.draw.circle(screen, WHITE, (bx + 12, by - 5), 8)
        pygame.draw.circle(screen, BLACK, (bx - 12, by - 5), 4)
        pygame.draw.circle(screen, BLACK, (bx + 12, by - 5), 4)

        draw_text(boss_name, ARENA.left, 14, ORANGE, BIG)
        hp_bar = pygame.Rect(ARENA.left, 85, ARENA.width, 24)
        pygame.draw.rect(screen, (65, 30, 45), hp_bar)
        hp_ratio = max(0, boss_hp / boss_max_hp)
        pygame.draw.rect(screen, boss_color, (hp_bar.x, hp_bar.y, int(hp_bar.width * hp_ratio), hp_bar.height))
        pygame.draw.rect(screen, WHITE, hp_bar, 2)
        draw_text(f"CURRENT PATTERN: {current_pattern_name}", ARENA.right - 500, 120, YELLOW, SMALL)

    elif stage == 2:
        display_boss_color = YELLOW if final_exam_active else ((80, 230, 255) if logic_boss_blue else (255, 110, 45))
        pygame.draw.circle(screen, display_boss_color, (bx, by), int(35 + pulse))
        pygame.draw.circle(screen, WHITE, (bx - 12, by - 5), 7)
        pygame.draw.circle(screen, WHITE, (bx + 12, by - 5), 7)
        pygame.draw.circle(screen, BLACK, (bx - 12, by - 5), 3)
        pygame.draw.circle(screen, BLACK, (bx + 12, by - 5), 3)

        if boss_dialogue[1] > 0:
            diag_surf = BIG.render(boss_dialogue[0], True, YELLOW if final_exam_active else GREEN)
            screen.blit(diag_surf, (bx - diag_surf.get_width() // 2, by - 110))

        draw_text("수학의 지배자 - STAGE 2", ARENA.left, ARENA.top - 140, WHITE, BIG)
        draw_text("π", bx - 65, by - 38, PURPLE, BIG)
        draw_text("√x", bx + 35, by - 38, YELLOW, FONT)

        panel = pygame.Rect(ARENA.right - 520, ARENA.top - 135, 520, 100)
        pygame.draw.rect(screen, (27, 25, 48), panel, border_radius=10)
        pygame.draw.rect(screen, YELLOW if logic_round_active else (90, 85, 125), panel, 2, border_radius=10)
        statement = LOGIC_FORMS[logic_form_index]
        draw_text(statement, panel.x + 20, panel.y + 35, YELLOW, LOGIC_FONT)
        seconds_left = max(0, logic_timer // 60 + 1)
        draw_text(f"{seconds_left}s", panel.x + 465, panel.y + 35, WHITE, SMALL_FONT)

        if logic_feedback_timer > 0:
            draw_text(logic_feedback, panel.x + 20, panel.y + 70, GREEN if "정답" in logic_feedback else RED, SMALL_FONT)

        pygame.draw.rect(screen, (65, 30, 45), (ARENA.left, ARENA.top - 45, ARENA.width, 22))
        pygame.draw.rect(screen, CYAN, (ARENA.left, ARENA.top - 45, max(0, int(ARENA.width * math_boss_hp / math_boss_max_hp)), 22))

    draw_text("PLAYER HP", ARENA.left, 120, RED, SMALL)
    for i in range(5):
        color = RED if i < player.hp else (65, 35, 45)
        pygame.draw.rect(screen, color, (ARENA.left + 150 + i * 38, 124, 30, 18), border_radius=3)

    if stage == 1 and quiz_active and quiz_word:
        panel = pygame.Rect(ARENA.centerx - 300, ARENA.centery - 190, 600, 380)
        pygame.draw.rect(screen, (27, 25, 48), panel, border_radius=14)
        pygame.draw.rect(screen, YELLOW, panel, 3, border_radius=14)

        title = SMALL.render("영단어 퀴즈 (초등 + 고난도)", True, YELLOW)
        screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 40)))

        word_image = WORD_FONT.render(quiz_word[0], True, CYAN)
        screen.blit(word_image, word_image.get_rect(center=(panel.centerx, panel.y + 100)))

        instruction = SMALL.render("뜻을 선택하세요! (1 / 2 / 3 / 4)", True, WHITE)
        screen.blit(instruction, instruction.get_rect(center=(panel.centerx, panel.y + 150)))

        for i, meaning in enumerate(quiz_choices):
            draw_text(f"{i + 1}. {meaning}", panel.x + 80, panel.y + 195 + i * 40, WHITE, SMALL)

        bar_x, bar_y, bar_w, bar_h = ARENA.left, ARENA.bottom + 12, ARENA.width, 16
        time_ratio = max(0.0, min(1.0, quiz_timer / 300))
        remaining_w = int(bar_w * time_ratio)
        bar_color = GREEN if time_ratio > 0.5 else (ORANGE if time_ratio > 0.2 else RED)
        pygame.draw.rect(screen, (55, 30, 45), (bar_x, bar_y, bar_w, bar_h))
        if remaining_w > 0:
            pygame.draw.rect(screen, bar_color, (bar_x, bar_y, remaining_w, bar_h))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)

    elif stage == 1 and quiz_feedback_timer > 0:
        color = GREEN if "정답" in quiz_feedback else RED
        feedback_image = SMALL.render(quiz_feedback, True, color)
        screen.blit(feedback_image, feedback_image.get_rect(center=(ARENA.centerx, ARENA.top - 15)))


# =========================
# 메인 게임 루프
# =========================
frame = 0
running = True
pygame.key.start_text_input()

while running:
    clock.tick(60)
    frame += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                break

            if screen_mode == "input":
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if player_name.strip() and student_id.strip():
                        pygame.key.stop_text_input()
                        screen_mode = "tutorial"
                elif event.key == pygame.K_BACKSPACE:
                    if active_input == "name":
                        player_name = player_name[:-1]
                    else:
                        student_id = student_id[:-1]
                elif event.key in (pygame.K_TAB, pygame.K_UP, pygame.K_DOWN):
                    active_input = "student_id" if active_input == "name" else "name"

            elif screen_mode == "tutorial":
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    init_game()
                    screen_mode = "playing"

            elif screen_mode == "playing":
                if event.key == pygame.K_SPACE:
                    player.do_jump()

                if stage == 1 and quiz_active:
                    key_map = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3,
                               pygame.K_KP1: 0, pygame.K_KP2: 1, pygame.K_KP3: 2, pygame.K_KP4: 3}
                    if event.key in key_map:
                        finish_english_quiz(key_map[event.key] == quiz_answer)

                elif stage == 2 and logic_round_active and not final_exam_active:
                    if event.key == pygame.K_z or event.key == pygame.K_u:
                        if logic_should_attack:
                            finish_logic_round(True, "정답! 공격 준비 완료")
                        else:
                            finish_logic_round(False, "오답! 보스 회복 모드")

                if event.key in (pygame.K_u, pygame.K_z):
                    if stage == 1 and not quiz_active:
                        if player.shoot_cooldown <= 0:
                            shots.append(Shot(player.x, player.y - player.jump))
                            player.shoot_cooldown = 12
                    elif stage == 2 and not final_exam_active:
                        if player.shoot_cooldown <= 0:
                            shots.append(Shot(player.x, player.y - player.jump))
                            player.shoot_cooldown = 10

            elif screen_mode == "stage1_clear":
                if event.key == pygame.K_RETURN:
                    screen_mode = "stage2_ready"
                    bullets.clear()
                    shots.clear()

            elif screen_mode == "stage2_ready":
                if event.key == pygame.K_RETURN:
                    screen_mode = "playing"
                    stage = 2
                    start_logic_round()

            elif screen_mode == "ranking":
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    screen_mode = "input"
                    player_name = ""
                    student_id = ""
                    pygame.key.start_text_input()

        if screen_mode == "input" and event.type == pygame.TEXTINPUT:
            if active_input == "name" and len(player_name) < 12:
                player_name += event.text
            elif active_input == "student_id" and len(student_id) < 15 and event.text.isdigit():
                student_id += event.text

        if screen_mode == "input" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if name_box_rect.collidepoint(event.pos):
                active_input = "name"
            elif id_box_rect.collidepoint(event.pos):
                active_input = "student_id"
            elif start_button_rect.collidepoint(event.pos):
                if player_name.strip() and student_id.strip():
                    pygame.key.stop_text_input()
                    screen_mode = "tutorial"

        if screen_mode == "tutorial" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            btn_rect = pygame.Rect(W // 2 - 250, 715, 500, 60)
            if btn_rect.collidepoint(event.pos):
                init_game()
                screen_mode = "playing"

        if screen_mode == "ranking" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if restart_button.collidepoint(event.pos):
                screen_mode = "input"
                player_name = ""
                student_id = ""
                pygame.key.start_text_input()

    if not running:
        break

    # =========================
    # 게임 플레이 로직 업데이트
    # =========================
    if screen_mode == "playing":
        keys = pygame.key.get_pressed()
        player.update(keys)

        if stage == 1:
            if quiz_feedback_timer > 0: quiz_feedback_timer -= 1

            if quiz_active:
                quiz_timer -= 1
                if quiz_timer <= 0: finish_english_quiz(False)
            else:
                quiz_cooldown -= 1
                if quiz_cooldown <= 0: start_english_quiz()

                pattern_timer_1 += 1
                pattern_timer_2 += 1
                if pattern_timer_1 >= max(78, int(169 / 1.2)):
                    pattern_timer_1 = 0
                    spawn_random_pattern()
                if pattern_timer_2 >= max(117, int(221 / 1.2)):
                    pattern_timer_2 = 0
                    spawn_random_pattern()

                passive_shoot_timer += 1
                if passive_shoot_timer >= 42:
                    passive_shoot_timer = 0
                    angle = aim_angle(ARENA.centerx, ARENA.top - 60, player.x, player.y - player.jump)
                    add_bullet(ARENA.centerx, ARENA.top - 60, angle, 4.2, RED, radius=8)

            for shot in shots[:]:
                shot.update()
                if shot.y < 0:
                    shots.remove(shot)
                    continue
                if math.hypot(shot.x - ARENA.centerx, shot.y - (ARENA.top - 60)) < 43:
                    shots.remove(shot)
                    boss_hp -= 4

            if boss_hp <= 0:
                boss_hp = 0
                bullets.clear()
                shots.clear()
                screen_mode = "stage1_clear"

        elif stage == 2:
            if boss_dialogue[1] > 0: boss_dialogue[1] -= 1

            if math_boss_hp <= 0 and not final_exam_active:
                final_exam_active = True
                final_exam_step = 1
                exam_phase = "waiting"
                target_quadrant = random.randint(1, 4)
                final_exam_timer = 180
                bullets.clear()
                factor_bullets.clear()
                circle_hazards.clear()
                giant_bullet.active = False
                boss_dialogue[0] = f"제{target_quadrant}사분면!"
                boss_dialogue[1] = 180

            if final_exam_active:
                final_exam_timer -= 1
                if exam_phase == "waiting":
                    if final_exam_timer <= 0:
                        exam_phase = "checking"
                        final_exam_timer = 60
                        boss_dialogue[0] = "쾅!"
                        boss_dialogue[1] = 60
                elif exam_phase == "checking":
                    if final_exam_timer <= 0:
                        px, py = player.x, player.y
                        cx, cy = ARENA.centerx, ARENA.centery
                        in_target = (
                            (target_quadrant == 1 and px >= cx and py <= cy) or
                            (target_quadrant == 2 and px <= cx and py <= cy) or
                            (target_quadrant == 3 and px <= cx and py >= cy) or
                            (target_quadrant == 4 and px >= cx and py >= cy)
                        )

                        if not in_target and player.jump_time <= 0 and player.invincible <= 0:
                            player.hp -= 1
                            player.invincible = 60
                            if player.hp <= 0:
                                record_result("Lose", 2, math_boss_hp, 0)
                                screen_mode = "ranking"
                                pygame.key.start_text_input()

                        final_exam_step += 1
                        if final_exam_step > 4:
                            record_result("Clear", 2, 0, player.hp)
                            screen_mode = "ranking"
                            pygame.key.start_text_input()
                        else:
                            exam_phase = "waiting"
                            target_quadrant = random.randint(1, 4)
                            final_exam_timer = 90
                            boss_dialogue[0] = f"제{target_quadrant}사분면!"
                            boss_dialogue[1] = 90

            else:
                is_phase2 = math_boss_hp <= math_boss_max_hp / 2
                speed_mult = 1.3 if is_phase2 else 1.0

                if logic_feedback_timer > 0: logic_feedback_timer -= 1
                if logic_round_active:
                    logic_timer -= 1
                    if logic_timer <= 0: start_logic_round()

                giant_bullet.update()

                boss_shoot_timer += 1
                if boss_shoot_timer >= 60:
                    boss_shoot_timer = 0
                    angle = aim_angle(ARENA.centerx, ARENA.top - 60, player.x, player.y - player.jump)
                    bullets.append(Bullet(ARENA.centerx, ARENA.top - 60, math.cos(angle) * (4.5 * speed_mult), math.sin(angle) * (4.5 * speed_mult), ORANGE, radius=10, life=300))

                factor_spawn_timer += 1
                if factor_spawn_timer >= 210:
                    factor_spawn_timer = 0
                    base_angle = aim_angle(ARENA.centerx, ARENA.top - 60, player.x, player.y - player.jump)
                    for spread in [-0.25, 0.0, 0.25]:
                        factor_bullets.append(FactorBullet(ARENA.centerx, ARENA.top - 60, math.cos(base_angle + spread) * (3.5 * speed_mult), math.sin(base_angle + spread) * (3.5 * speed_mult)))

                for fb in factor_bullets[:]:
                    if fb.update(bullets, boss_dialogue, speed_mult): factor_bullets.remove(fb)

                circle_spawn_timer += 1
                if circle_spawn_timer >= (100 if is_phase2 else 150):
                    circle_spawn_timer = 0
                    ch = CirclePatternHazard()
                    circle_hazards.append(ch)
                    if is_phase2: circle_hazards.append(CirclePatternHazard(2 * ARENA.centerx - ch.x, 2 * ARENA.centery - ch.y))

                for ch in circle_hazards[:]:
                    ch.update(bullets, speed_mult)
                    if ch.exploded: circle_hazards.remove(ch)

                for shot in shots[:]:
                    shot.update()
                    if shot.y < 0:
                        shots.remove(shot)
                        continue
                    if math.hypot(shot.x - ARENA.centerx, shot.y - (ARENA.top - 60)) < 40:
                        shots.remove(shot)
                        if logic_failed_state:
                            math_boss_hp = min(math_boss_max_hp, math_boss_hp + 20)
                            logic_failed_state = False
                        else:
                            math_boss_hp -= 10

                if math_boss_hp > math_boss_max_hp: math_boss_hp = math_boss_max_hp

                if player.jump == 0:
                    distance = math.hypot(giant_bullet.x - player.x, giant_bullet.y - player.y)
                    if distance < giant_bullet.r + player.r and player.invincible <= 0 and player.jump_time <= 0:
                        player.hp -= 1
                        player.invincible = 60
                        if player.hp <= 0:
                            record_result("Lose", 2, math_boss_hp, 0)
                            screen_mode = "ranking"
                            pygame.key.start_text_input()

        for bullet in bullets[:]:
            bullet.update()
            if not bullet.alive():
                bullets.remove(bullet)
                continue
            if bullet.ground and player.jump_time > 0: continue

            distance = math.hypot(bullet.x - player.x, bullet.y - (player.y - player.jump))
            if distance < bullet.r + player.r:
                bullets.remove(bullet)
                if player.jump_time <= 0 and player.invincible <= 0:
                    player.hp -= 1
                    player.invincible = 75
                    if player.hp <= 0:
                        dead_boss_hp = boss_hp if stage == 1 else math_boss_hp
                        record_result("Lose", stage, dead_boss_hp, 0)
                        screen_mode = "ranking"
                        pygame.key.start_text_input()

    # =========================
    # 화면 렌더링 분기
    # =========================
    if screen_mode == "input":
        draw_input_screen()
    elif screen_mode == "tutorial":
        draw_tutorial_screen()
    elif screen_mode == "ranking":
        draw_ranking_screen()
    else:
        draw_arena()
        if stage == 2:
            for ch in circle_hazards: ch.draw()
            for fb in factor_bullets: fb.draw()
        for bullet in bullets: bullet.draw()
        for shot in shots: shot.draw()
        if stage == 2: giant_bullet.draw()
        player.draw()

        draw_text("MOVE: WASD/ARROWS    JUMP: SPACE (무적!)    ATTACK: U / Z", ARENA.left, 1020, CYAN, SMALL)
        if stage == 1:
            draw_text("QUIZ: 1-4 / NUMPAD 1-4", ARENA.left, 1050, YELLOW, SMALL)
        elif stage == 2 and not final_exam_active:
            draw_text("LOGIC QUIZ: PRESS U / Z (정답 공격)", ARENA.left, 1050, YELLOW, SMALL)

        if screen_mode == "stage1_clear":
            screen.fill(BLACK)
            draw_text("STAGE 1 CLEAR!", W // 2 - 200, H // 2 - 100, YELLOW, BIG)
            draw_text("영어 마스터를 물리쳤습니다!", W // 2 - 180, H // 2 - 20, WHITE, FONT)
            draw_text("ENTER를 눌러 수학의 지배자에게 향하세요!", W // 2 - 280, H // 2 + 50, CYAN, FONT)

        elif screen_mode == "stage2_ready":
            screen.fill(BLACK)
            draw_text("STAGE 2: 수학의 지배자", W // 2 - 230, H // 2 - 100, RED, BIG)
            draw_text("명제 퀴즈와 4사분면 최종 시험이 기다립니다.", W // 2 - 270, H // 2 - 20, WHITE, FONT)
            draw_text("ENTER를 눌러 전투를 시작하세요!", W // 2 - 220, H // 2 + 50, YELLOW, FONT)

    pygame.display.flip()

pygame.quit()