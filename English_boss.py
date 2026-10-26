import math
import random
import pygame

pygame.init()

# =========================
# 기본 설정 - 1920 x 1080 UI
# =========================
W, H = 1920, 1080
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("SOUL JUMP - 영어 보스")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("malgungothic", 34)
BIG = pygame.font.SysFont("malgungothic", 54, bold=True)
SMALL = pygame.font.SysFont("malgungothic", 26)
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

# 두 번째 코드의 중앙 전투장 배치
ARENA = pygame.Rect(310, 240, 1300, 700)

BOSS = {
    "name": "영어 마스터",
    "color": (255, 190, 70),
    "hp": 300,
    "speed": 1.2,
}

PATTERN_COUNT = 13
QUIZ_TIME_MAX = 300

BOSS_X = ARENA.centerx
BOSS_Y = ARENA.top - 60

# =========================
# 영어 단어 퀴즈
# =========================
WORDS = [
    ("apple", "사과"),
    ("brave", "용감한"),
    ("dream", "꿈"),
    ("journey", "여행"),
    ("wisdom", "지혜"),
    ("courage", "용기"),
    ("freedom", "자유"),
    ("victory", "승리"),
    ("ancient", "고대의"),
    ("discover", "발견하다"),
    ("protect", "보호하다"),
    ("improve", "향상시키다"),
    ("challenge", "도전"),
    ("knowledge", "지식"),
    ("imagine", "상상하다"),
]


# =========================
# 플레이어
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

        dx = (
            int(keys[pygame.K_RIGHT] or keys[pygame.K_d])
            - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        )
        dy = (
            int(keys[pygame.K_DOWN] or keys[pygame.K_s])
            - int(keys[pygame.K_UP] or keys[pygame.K_w])
        )

        # 대각선 이동 속도 보정
        if dx != 0 and dy != 0:
            speed_factor = 1 / math.sqrt(2)
        else:
            speed_factor = 1

        self.x += dx * speed * speed_factor
        self.y += dy * speed * speed_factor

        self.x = max(
            ARENA.left + 20,
            min(ARENA.right - 20, self.x)
        )
        self.y = max(
            ARENA.top + 20,
            min(ARENA.bottom - 20, self.y)
        )

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
        pygame.draw.ellipse(
            screen,
            (65, 55, 80),
            (self.x - 18, self.y - 7, 36, 14)
        )

        draw_y = int(self.y - self.jump)

        if self.invincible > 0 and (self.invincible // 4) % 2 == 0:
            return

        points = [
            (self.x, draw_y - 20),
            (self.x + 18, draw_y - 4),
            (self.x + 13, draw_y + 13),
            (self.x, draw_y + 20),
            (self.x - 13, draw_y + 13),
            (self.x - 18, draw_y - 4),
        ]

        pygame.draw.polygon(screen, RED, points)
        pygame.draw.circle(
            screen, WHITE,
            (int(self.x - 5), int(draw_y - 2)), 4
        )
        pygame.draw.circle(
            screen, WHITE,
            (int(self.x + 5), int(draw_y - 2)), 4
        )


# =========================
# 일반 탄환
# =========================
class Bullet:
    def __init__(
        self, x, y, vx, vy, color,
        radius=9, ground=False, life=360, ax=0, ay=0
    ):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.ax = ax
        self.ay = ay
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
        pygame.draw.circle(
            screen, self.color,
            (int(self.x), int(self.y)), self.r
        )
        pygame.draw.circle(
            screen, WHITE,
            (int(self.x - 2), int(self.y - 2)),
            max(1, self.r // 3)
        )

    def alive(self):
        return (
            self.life > 0
            and -50 < self.x < W + 50
            and -60 < self.y < H + 60
        )


# =========================
# 글자 탄환
# =========================
class WordBullet(Bullet):
    def __init__(self, x, y, vx, vy, word, color):
        super().__init__(
            x, y, vx, vy, color,
            radius=11, ground=False, life=300
        )
        self.word = word

    def draw(self):
        image = WORD_BULLET_FONT.render(
            self.word, True, self.color
        )
        rect = image.get_rect(
            center=(int(self.x), int(self.y))
        )
        screen.blit(image, rect)


# =========================
# 플레이어 공격
# =========================
class Shot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = -10
        self.r = 7

    def update(self):
        self.y += self.vy

    def draw(self):
        pygame.draw.circle(
            screen, CYAN,
            (int(self.x), int(self.y)), self.r
        )
        pygame.draw.circle(
            screen, WHITE,
            (int(self.x), int(self.y)), 3
        )


# =========================
# 게임 상태
# =========================
player = Player()
bullets = []
shots = []

boss_hp = BOSS["hp"]
boss_max_hp = boss_hp

frame = 0
pattern_timer = 0
pattern_index = 0
current_pattern_name = "VOCABULARY TEST"

game_state = "playing"

quiz_active = False
quiz_timer = 0
quiz_cooldown = 100
quiz_feedback = ""
quiz_feedback_timer = 0
quiz_word = None
quiz_choices = []
quiz_answer = 0


# =========================
# 탄막 생성 도구
# =========================
def add_bullet(
    x, y, angle, speed, color,
    radius=9, ground=False, ax=0, ay=0
):
    vx = math.cos(angle) * speed
    vy = math.sin(angle) * speed

    bullets.append(
        Bullet(
            x, y, vx, vy, color,
            radius, ground, 360, ax, ay
        )
    )


def aim_angle(x1, y1, x2, y2):
    return math.atan2(y2 - y1, x2 - x1)


def add_word_bullet(
    x, y, angle, speed, word=None, color=None
):
    if word is None:
        word = random.choice(WORDS)[0]

    if color is None:
        color = random.choice([CYAN, PURPLE, PINK, ORANGE])

    bullets.append(
        WordBullet(
            x, y,
            math.cos(angle) * speed,
            math.sin(angle) * speed,
            word, color
        )
    )


# =========================
# 보스 패턴 13종
# =========================
def spawn_pattern():
    global pattern_index, current_pattern_name

    p = pattern_index

    left = ARENA.left + 15
    right = ARENA.right - 15
    top = ARENA.top + 15
    bottom = ARENA.bottom - 15

    boss_x, boss_y = BOSS_X, BOSS_Y

    # 1. 알파벳 비
    if p == 0:
        current_pattern_name = "ALPHABET RAIN"

        for _ in range(24):
            x = random.randint(left, right)
            y = random.randint(top - 120, top)

            add_bullet(
                x, y, math.pi / 2,
                random.uniform(3.0, 4.5),
                CYAN, radius=8
            )

    # 2. 문법 십자
    elif p == 1:
        current_pattern_name = "GRAMMAR CROSS"

        for i in range(9):
            y = top + i * 70

            if y < bottom:
                add_bullet(
                    left, y, 0, 3.5,
                    YELLOW, radius=9
                )
                add_bullet(
                    right, y, math.pi, 3.5,
                    PURPLE, radius=9
                )

    # 3. 글자 고리
    elif p == 2:
        current_pattern_name = "ASGORE LETTER RING"

        letters = ["A", "E", "R", "S", "T", "O", "N"]
        ring_count = 7
        letters_per_ring = 4

        for ring in range(ring_count):
            base_angle = (
                math.pi / 2
                + ring * math.tau / ring_count
            )
            offset = math.pi / 18 if ring % 2 else 0

            for j in range(letters_per_ring):
                spread = (
                    j - (letters_per_ring - 1) / 2
                ) * 0.12

                angle = base_angle + offset + spread
                word = random.choice(letters)
                color = ORANGE if ring % 2 == 0 else PINK
                speed = 3.0 + (j % 2) * 0.4

                add_word_bullet(
                    boss_x, boss_y,
                    angle, speed, word, color
                )

    # 4. 문장부호 폭풍
    elif p == 3:
        current_pattern_name = "PUNCTUATION STORM"

        for i in range(8):
            x = left + i * (right - left) / 7

            add_bullet(
                x, top,
                math.pi / 2 + 0.15,
                4.0, RED, radius=9
            )

            add_bullet(
                right - (x - left), bottom,
                -math.pi / 2 - 0.15,
                4.0, GREEN, radius=9
            )

    # 5. 문장 파도
    elif p == 4:
        current_pattern_name = "SENTENCE WAVE"

        for i in range(13):
            y = top + i * 50

            if y > bottom:
                break

            direction = 1 if i % 2 == 0 else -1

            bullets.append(
                Bullet(
                    left if direction == 1 else right,
                    y,
                    direction * 3.0,
                    0,
                    CYAN if direction == 1 else PURPLE,
                    radius=8,
                    ax=0,
                    ay=math.sin(i) * 0.035
                )
            )

    # 6. 지혜의 영혼
    elif p == 5:
        current_pattern_name = "WISDOM SOUL"

        source_y = ARENA.centery
        left_x = ARENA.left + 35
        right_x = ARENA.right - 35

        for i in range(5):
            spread = (i - 2) * 0.14
            speed = 3.2 + (i % 2) * 0.4

            left_angle = (
                aim_angle(
                    left_x, source_y,
                    player.x, player.y
                ) + spread
            )

            add_word_bullet(
                left_x, source_y,
                left_angle, speed, color=PURPLE
            )

            right_angle = (
                aim_angle(
                    right_x, source_y,
                    player.x, player.y
                ) - spread
            )

            add_word_bullet(
                right_x, source_y,
                right_angle, speed, color=CYAN
            )

    # 7. 꽃 모양 나선 탄막
    elif p == 6:
        current_pattern_name = "FLOWER SPIRAL"

        cx, cy = ARENA.centerx, ARENA.top + 100
        petal_count = 8
        bullets_per_petal = 3
        rotation = frame * 0.018

        for petal in range(petal_count):
            base_angle = (
                math.tau * petal / petal_count
                + rotation
            )

            for j in range(bullets_per_petal):
                angle = base_angle + (j - 1) * 0.10
                speed = 2.5 + j * 0.35

                add_bullet(
                    cx, cy, angle, speed,
                    GREEN if petal % 2 == 0 else PINK,
                    radius=8
                )

    # 8. 최종 시험
    elif p == 7:
        current_pattern_name = "FINAL EXAM"

        for i in range(11):
            x = left + i * (right - left) / 10
            direction = 1 if i % 2 == 0 else -1

            bullets.append(
                Bullet(
                    x, top,
                    direction * 1.1, 3.2,
                    ORANGE, radius=9,
                    ax=-direction * 0.025
                )
            )

            bullets.append(
                Bullet(
                    x, bottom,
                    -direction * 1.1, -3.2,
                    CYAN, radius=9,
                    ax=direction * 0.025
                )
            )

    # 9. 부채꼴 탄막
    elif p == 8:
        current_pattern_name = "FAN SHOT"

        count = 11
        center_angle = aim_angle(
            boss_x, boss_y,
            player.x, player.y
        )
        spread = math.radians(58)

        for i in range(count):
            angle = (
                center_angle - spread / 2
                + spread * i / (count - 1)
            )

            add_bullet(
                boss_x, boss_y,
                angle, 3.4, ORANGE, radius=9
            )

    # 10. 지그재그
    elif p == 9:
        current_pattern_name = "ZIGZAG DANCE"

        for i in range(10):
            y = top + i * 60

            if y > bottom:
                break

            direction = 1 if i % 2 == 0 else -1
            start_x = left if direction == 1 else right

            bullets.append(
                Bullet(
                    start_x, y,
                    direction * 3.5, 0,
                    PINK if direction == 1 else CYAN,
                    radius=9,
                    ay=0.045 if i % 2 == 0 else -0.045
                )
            )

    # 11. 플레이어 조준 연사
    elif p == 10:
        current_pattern_name = "TARGET BURST"

        base_angle = aim_angle(
            boss_x, boss_y,
            player.x, player.y - player.jump
        )

        for offset in [-0.18, 0, 0.18]:
            add_bullet(
                boss_x, boss_y,
                base_angle + offset,
                4.0, RED, radius=9
            )

    # 12. 회전 십자
    elif p == 11:
        current_pattern_name = "ROTATING CROSS"

        cx, cy = ARENA.centerx, ARENA.top + 100
        count = 8

        for i in range(count):
            angle = math.tau * i / count + frame * 0.045

            add_bullet(
                cx, cy, angle, 3.0,
                PURPLE if i % 2 == 0 else CYAN,
                radius=9
            )

    # 13. 양쪽 포물선
    else:
        current_pattern_name = "DOUBLE ARC"

        for i in range(7):
            y = ARENA.top + 50 + i * 90

            bullets.append(
                Bullet(
                    left, y,
                    3.0, -0.15 + i * 0.045,
                    YELLOW, radius=9,
                    ay=0.025
                )
            )

            bullets.append(
                Bullet(
                    right, y,
                    -3.0, 0.15 - i * 0.045,
                    GREEN, radius=9,
                    ay=-0.025
                )
            )

    pattern_index = (pattern_index + 1) % PATTERN_COUNT


# =========================
# 영어 퀴즈 시스템
# =========================
def start_quiz():
    global quiz_active, quiz_timer
    global quiz_word, quiz_choices, quiz_answer

    quiz_word = random.choice(WORDS)
    correct_meaning = quiz_word[1]

    wrong_meanings = [
        meaning for word, meaning in WORDS
        if meaning != correct_meaning
    ]

    choices = random.sample(wrong_meanings, 3)
    choices.append(correct_meaning)
    random.shuffle(choices)

    quiz_choices = choices
    quiz_answer = choices.index(correct_meaning)

    quiz_active = True
    quiz_timer = QUIZ_TIME_MAX


def finish_quiz(correct):
    global quiz_active, quiz_cooldown
    global quiz_feedback, quiz_feedback_timer, boss_hp
    global game_state

    if not quiz_active:
        return

    quiz_active = False
    quiz_cooldown = 300
    quiz_feedback_timer = 90

    if correct:
        quiz_feedback = "정답! 보스 HP -20"
        boss_hp -= 20
    else:
        quiz_feedback = "오답! HP -1"

        if player.invincible <= 0:
            player.hp -= 1
            player.invincible = 75

            if player.hp <= 0:
                player.hp = 0
                game_state = "lose"


# =========================
# 텍스트 출력
# =========================
def draw_text(text, x, y, color=WHITE, font=FONT):
    image = font.render(str(text), True, color)
    screen.blit(image, (int(x), int(y)))


# =========================
# 화면 그리기
# =========================
def draw_arena():
    screen.fill(BLACK)

    # 배경 별
    for i in range(75):
        x = (i * 173 + 41) % W
        y = (i * 97 + 29) % H
        pygame.draw.circle(
            screen, (45, 40, 70),
            (x, y), 1
        )

    # 전투장
    pygame.draw.rect(screen, (20, 15, 35), ARENA)

    for gx in range(ARENA.left + 50, ARENA.right, 50):
        pygame.draw.line(
            screen, (32, 35, 65),
            (gx, ARENA.top),
            (gx, ARENA.bottom), 1
        )

    for gy in range(ARENA.top + 50, ARENA.bottom, 50):
        pygame.draw.line(
            screen, (32, 35, 65),
            (ARENA.left, gy),
            (ARENA.right, gy), 1
        )

    pygame.draw.rect(screen, WHITE, ARENA, 4)

    # 보스
    pulse = math.sin(frame * 0.06) * 6
    bx, by = BOSS_X, BOSS_Y

    pygame.draw.circle(
        screen, BOSS["color"],
        (bx, by), int(35 + pulse)
    )
    pygame.draw.circle(
        screen, WHITE, (bx - 12, by - 5), 8
    )
    pygame.draw.circle(
        screen, WHITE, (bx + 12, by - 5), 8
    )
    pygame.draw.circle(
        screen, BLACK, (bx - 12, by - 5), 4
    )
    pygame.draw.circle(
        screen, BLACK, (bx + 12, by - 5), 4
    )

    # 상단 UI - 텍스트 내용 유지
    draw_text(
        "영어 마스터",
        ARENA.left, 14, ORANGE, BIG
    )

    # 보스 체력 바
    hp_bar = pygame.Rect(
        ARENA.left, 85, ARENA.width, 24
    )

    pygame.draw.rect(
        screen, (65, 30, 45), hp_bar
    )

    hp_ratio = max(0, boss_hp / boss_max_hp)

    pygame.draw.rect(
        screen, BOSS["color"],
        (
            hp_bar.x,
            hp_bar.y,
            int(hp_bar.width * hp_ratio),
            hp_bar.height
        )
    )

    pygame.draw.rect(screen, WHITE, hp_bar, 2)

    # 플레이어 HP
    draw_text(
        "PLAYER HP",
        ARENA.left, 120, RED, SMALL
    )

    for i in range(5):
        color = RED if i < player.hp else (65, 35, 45)

        pygame.draw.rect(
            screen, color,
            (ARENA.left + 150 + i * 38, 124, 30, 18),
            border_radius=3
        )

    # 패턴 표시
    shown_pattern = pattern_index + 1

    if shown_pattern > PATTERN_COUNT:
        shown_pattern = 1

    draw_text(
        f"PATTERN {shown_pattern}/{PATTERN_COUNT}",
        ARENA.right - 360, 120, YELLOW, SMALL
    )

    draw_text(
        current_pattern_name,
        ARENA.left, 170, CYAN, SMALL
    )

    # 퀴즈 패널
    # 전투장 중심 기준으로 배치해 UI 크기 변경에도 중앙 유지
    if quiz_active and quiz_word:
        panel = pygame.Rect(
            ARENA.centerx - 300,
            ARENA.centery - 190,
            600, 380
        )

        pygame.draw.rect(
            screen, (27, 25, 48),
            panel, border_radius=14
        )
        pygame.draw.rect(
            screen, YELLOW,
            panel, 3, border_radius=14
        )

        title = SMALL.render(
            "단어 문제", True, YELLOW
        )
        screen.blit(
            title,
            title.get_rect(
                center=(panel.centerx, panel.y + 40)
            )
        )

        word_image = WORD_FONT.render(
            quiz_word[0], True, CYAN
        )
        screen.blit(
            word_image,
            word_image.get_rect(
                center=(panel.centerx, panel.y + 100)
            )
        )

        instruction = SMALL.render(
            "뜻을 선택하세요! (1 / 2 / 3 / 4)",
            True, WHITE
        )
        screen.blit(
            instruction,
            instruction.get_rect(
                center=(panel.centerx, panel.y + 150)
            )
        )

        for i, meaning in enumerate(quiz_choices):
            draw_text(
                f"{i + 1}. {meaning}",
                panel.x + 80,
                panel.y + 195 + i * 40,
                WHITE, SMALL
            )

        # 퀴즈 타이머 바
        bar_x = ARENA.left
        bar_y = ARENA.bottom + 12
        bar_w = ARENA.width
        bar_h = 16

        time_ratio = max(
            0.0,
            min(1.0, quiz_timer / QUIZ_TIME_MAX)
        )
        remaining_w = int(bar_w * time_ratio)

        if time_ratio > 0.5:
            bar_color = GREEN
        elif time_ratio > 0.2:
            bar_color = ORANGE
        else:
            bar_color = RED

        pygame.draw.rect(
            screen, (55, 30, 45),
            (bar_x, bar_y, bar_w, bar_h)
        )

        if remaining_w > 0:
            pygame.draw.rect(
                screen, bar_color,
                (bar_x, bar_y, remaining_w, bar_h)
            )

        pygame.draw.rect(
            screen, WHITE,
            (bar_x, bar_y, bar_w, bar_h), 2
        )

        seconds_left = max(
            0, math.ceil(quiz_timer / 60)
        )

        timer_label = SMALL.render(
            f"TIME: {seconds_left}s",
            True, WHITE
        )

        screen.blit(
            timer_label,
            timer_label.get_rect(
                center=(ARENA.centerx, bar_y + 36)
            )
        )

    elif quiz_feedback_timer > 0:
        color = (
            GREEN if "정답" in quiz_feedback
            else RED
        )

        feedback_image = SMALL.render(
            quiz_feedback, True, color
        )

        screen.blit(
            feedback_image,
            feedback_image.get_rect(
                center=(ARENA.centerx, ARENA.top - 15)
            )
        )


# =========================
# 게임 재시작
# =========================
def restart_game():
    global player, bullets, shots
    global boss_hp, frame, pattern_timer, pattern_index
    global current_pattern_name, game_state
    global quiz_active, quiz_timer, quiz_cooldown
    global quiz_feedback, quiz_feedback_timer
    global quiz_word, quiz_choices, quiz_answer

    player = Player()
    bullets = []
    shots = []

    boss_hp = BOSS["hp"]

    frame = 0
    pattern_timer = 0
    pattern_index = 0
    current_pattern_name = "VOCABULARY TEST"

    quiz_active = False
    quiz_timer = 0
    quiz_cooldown = 100
    quiz_feedback = ""
    quiz_feedback_timer = 0
    quiz_word = None
    quiz_choices = []
    quiz_answer = 0

    game_state = "playing"


# =========================
# 메인 루프
# =========================
running = True

while running:
    clock.tick(60)
    frame += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if game_state == "playing":
                if event.key == pygame.K_SPACE:
                    player.do_jump()

                if quiz_active:
                    key_map = {
                        pygame.K_1: 0,
                        pygame.K_2: 1,
                        pygame.K_3: 2,
                        pygame.K_4: 3,
                        pygame.K_KP1: 0,
                        pygame.K_KP2: 1,
                        pygame.K_KP3: 2,
                        pygame.K_KP4: 3,
                    }

                    if event.key in key_map:
                        finish_quiz(
                            key_map[event.key] == quiz_answer
                        )

                elif event.key == pygame.K_u:
                    if player.shoot_cooldown <= 0:
                        shots.append(
                            Shot(
                                player.x,
                                player.y - player.jump
                            )
                        )
                        player.shoot_cooldown = 12

            elif event.key == pygame.K_RETURN:
                restart_game()

    # =========================
    # 게임 진행
    # =========================
    if game_state == "playing":
        keys = pygame.key.get_pressed()
        player.update(keys)

        if quiz_feedback_timer > 0:
            quiz_feedback_timer -= 1

        # 퀴즈 타이머 및 출제 주기 유지
        if quiz_active:
            quiz_timer -= 1

            if quiz_timer <= 0:
                finish_quiz(False)
        else:
            quiz_cooldown -= 1

            if quiz_cooldown <= 0:
                start_quiz()

        # 탄막 패턴 주기 유지
        pattern_timer += 1
        interval = max(
            65, int(150 / BOSS["speed"])
        )

        if pattern_timer >= interval:
            pattern_timer = 0
            spawn_pattern()

        # 플레이어 공격 판정
        for shot in shots[:]:
            shot.update()

            if shot.y < 0:
                shots.remove(shot)
                continue

            if math.hypot(
                shot.x - BOSS_X,
                shot.y - BOSS_Y
            ) < 43:
                shots.remove(shot)
                boss_hp -= 4

        if boss_hp <= 0:
            boss_hp = 0
            game_state = "win"

        # 탄막 충돌 판정
        for bullet in bullets[:]:
            bullet.update()

            if not bullet.alive():
                bullets.remove(bullet)
                continue

            if bullet.ground and player.jump_time > 0:
                continue

            distance = math.hypot(
                bullet.x - player.x,
                bullet.y - (player.y - player.jump)
            )

            if distance < bullet.r + player.r:
                bullets.remove(bullet)

                if player.invincible <= 0:
                    player.hp -= 1
                    player.invincible = 75

                    if player.hp <= 0:
                        player.hp = 0
                        game_state = "lose"

    # =========================
    # 렌더링
    # =========================
    draw_arena()

    for bullet in bullets:
        bullet.draw()

    for shot in shots:
        shot.draw()

    player.draw()

    # 조작 안내 텍스트 내용 유지
    draw_text(
        "MOVE: WASD/ARROWS   JUMP: SPACE   ATTACK: U",
        ARENA.left, 1020, CYAN, SMALL
    )

    draw_text(
        "QUIZ: 1-4 / NUMPAD 1-4",
        ARENA.left, 1050, YELLOW, SMALL
    )

    # 승리 화면
    if game_state == "win":
        screen.fill(BLACK)

        draw_text(
            "VICTORY!!",
            W // 2 - 180, H // 2 - 100,
            YELLOW, BIG
        )

        draw_text(
            "보스의 최종 시험을 완벽하게 돌파했습니다!",
            W // 2 - 350, H // 2,
            CYAN, FONT
        )

        draw_text(
            "ENTER: 다시 도전     ESC: 종료",
            W // 2 - 260, H // 2 + 80,
            WHITE, FONT
        )

    # 패배 화면
    elif game_state == "lose":
        screen.fill(BLACK)

        draw_text(
            "GAME OVER",
            W // 2 - 180, H // 2 - 100,
            RED, BIG
        )

        draw_text(
            "도전에 실패했습니다.",
            W // 2 - 150, H // 2,
            WHITE, FONT
        )

        draw_text(
            "ENTER: 다시 도전     ESC: 종료",
            W // 2 - 260, H // 2 + 80,
            WHITE, FONT
        )

    pygame.display.flip()

pygame.quit()
