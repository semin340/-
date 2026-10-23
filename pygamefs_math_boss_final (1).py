import math
import random
import pygame

pygame.init()

# =========================
# 기본 설정
# =========================
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("SOUL JUMP - 수학 보스")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("malgungothic", 22)
BIG = pygame.font.SysFont("malgungothic", 38, bold=True)

BLACK = (10, 8, 20)
WHITE = (245, 245, 255)
RED = (255, 65, 95)
CYAN = (80, 230, 255)
PURPLE = (175, 90, 255)
YELLOW = (255, 220, 80)
ORANGE = (255, 110, 45)
GREEN = (100, 255, 150)

ARENA = pygame.Rect(100, 145, 600, 385)

BOSSES = [
    {
        "name": "수학의 지배자",
        "color": (80, 230, 255),
        "hp": 260,
        "speed": 1.0,
    },
]

# =========================
# 게임 객체
# =========================
class Player:
    def __init__(self):
        self.x = 400
        self.y = 440
        self.r = 10
        self.hp = 5
        self.jump = 0
        self.jump_time = 0
        self.jump_cooldown = 0
        self.invincible = 0
        self.shoot_cooldown = 0

    def update(self, keys):
        speed = 4

        dx = (
            int(keys[pygame.K_RIGHT] or keys[pygame.K_d])
            - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        )
        dy = (
            int(keys[pygame.K_DOWN] or keys[pygame.K_s])
            - int(keys[pygame.K_UP] or keys[pygame.K_w])
        )

        self.x += dx * speed
        self.y += dy * speed

        self.x = max(ARENA.left + 14,
                     min(ARENA.right - 14, self.x))
        self.y = max(ARENA.top + 14,
                     min(ARENA.bottom - 14, self.y))

        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1

        if self.invincible > 0:
            self.invincible -= 1

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.jump_time > 0:
            self.jump_time -= 1
            # 점프 높이가 포물선처럼 변한다.
            t = 1 - self.jump_time / 32
            self.jump = math.sin(t * math.pi) * 48
        else:
            self.jump = 0

    def do_jump(self):
        if self.jump_cooldown <= 0 and self.jump_time <= 0:
            self.jump_time = 32
            self.jump_cooldown = 48

    def draw(self):
        # 점프 중에도 그림자는 바닥에 남는다.
        pygame.draw.ellipse(
            screen, (65, 55, 80),
            (self.x - 12, self.y - 5, 24, 10)
        )

        draw_y = int(self.y - self.jump)

        if self.invincible > 0 and (self.invincible // 4) % 2 == 0:
            return

        # 영혼 모양
        points = [
            (self.x, draw_y - 12),
            (self.x + 12, draw_y - 2),
            (self.x + 9, draw_y + 9),
            (self.x, draw_y + 14),
            (self.x - 9, draw_y + 9),
            (self.x - 12, draw_y - 2),
        ]
        pygame.draw.polygon(screen, RED, points)
        pygame.draw.circle(screen, WHITE,
                           (self.x - 3, draw_y), 2)
        pygame.draw.circle(screen, WHITE,
                           (self.x + 3, draw_y), 2)


class Bullet:
    def __init__(self, x, y, vx, vy, color,
                 radius=6, ground=True, life=360,
                 ax=0.0, ay=0.0):
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
            and -40 < self.x < W + 40
            and -50 < self.y < H + 50
        )


class Shot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = -8
        self.r = 5

    def update(self):
        self.y += self.vy

    def draw(self):
        pygame.draw.circle(
            screen, CYAN,
            (int(self.x), int(self.y)), self.r
        )

# =========================
# 전투 시스템
# =========================
player = Player()
bullets = []
shots = []

boss_index = 0  # 1·2단계를 삭제하고 수학 보스만 실행
boss_hp = BOSSES[boss_index]["hp"]
boss_max_hp = boss_hp

frame = 0
pattern_timer = 0
pattern_index = 0
current_pattern_name = "준비"
game_state = "playing"
message_timer = 0

# 명제 퀴즈 상태
logic_forms = [
    ("원명제", "보스가 파란색이면 공격"),
    ("역", "공격하면 보스가 파란색"),
    ("이", "보스가 파란색이 아니면 공격하지 않는다"),
    ("대우", "공격하지 않으면 보스가 파란색이 아니다"),
]
logic_round_active = False
logic_round_timer = 0
logic_cooldown = 120
logic_form_index = 0
logic_boss_blue = True
logic_should_attack = True
logic_feedback = ""
logic_feedback_timer = 0
LOGIC_FONT = pygame.font.SysFont("malgungothic", 17)
SMALL_FONT = pygame.font.SysFont("malgungothic", 15)

# 레이저 경고 위치
laser_x = None
laser_timer = 0

# =========================
# 탄막 생성 도구
# =========================
def add_bullet(x, y, angle, speed, color,
               radius=6, ground=True, life=360,
               ax=0.0, ay=0.0):
    vx = math.cos(angle) * speed
    vy = math.sin(angle) * speed

    bullets.append(Bullet(
        x, y, vx, vy, color, radius, ground, life, ax, ay
    ))


def aim_angle(x1, y1, x2, y2):
    return math.atan2(y2 - y1, x2 - x1)


def fan_attack(count, spread, speed, color, ground=True):
    angle = aim_angle(400, 95, player.x, player.y)
    for i in range(count):
        a = angle + (i - (count - 1) / 2) * spread
        add_bullet(400, 95, a, speed, color,
                   ground=ground)


def ring_attack(count, speed, color, offset=0,
                ground=True):
    for i in range(count):
        a = math.pi * 2 * i / count + offset
        add_bullet(400, 95, a, speed, color,
                   ground=ground)


def aimed_attack(count, speed, color, ground=False):
    for i in range(count):
        a = aim_angle(400, 95, player.x, player.y)
        a += random.uniform(-0.15, 0.15)
        add_bullet(400, 95, a, speed, color,
                   radius=7, ground=ground)


def edge_attack(count, speed, color):
    # 좌우에서 플레이어 쪽으로 날아오는 탄환
    for i in range(count):
        y = random.randint(ARENA.top + 15,
                           ARENA.bottom - 15)

        for x in (ARENA.left - 5, ARENA.right + 5):
            a = aim_angle(x, y, player.x, player.y)
            add_bullet(x, y, a, speed, color,
                       ground=True)


def rain_attack(count, color):
    for _ in range(count):
        x = random.randint(ARENA.left + 10,
                           ARENA.right - 10)
        y = ARENA.top - random.randint(10, 130)
        add_bullet(x, y, math.pi / 2,
                   random.uniform(3, 6), color,
                   ground=True)


def laser_attack():
    global laser_x, laser_timer
    laser_x = random.randint(
        ARENA.left + 25, ARENA.right - 25
    )
    laser_timer = 48


def spawn_pattern():
    """수학 개념을 경기장 전체의 공격 기믹으로 표현하는 8종 패턴."""
    global pattern_index, laser_x, laser_timer, current_pattern_name
    p = pattern_index
    left, right = ARENA.left + 8, ARENA.right - 8
    top, bottom = ARENA.top + 8, ARENA.bottom - 8

    # 1. 이차함수: 좌우에서 포물선 궤도로 휘어 들어오는 탄막
    if p == 0:
        current_pattern_name = "이차함수 | 포물선의 교차"
        for side in (0, 1):
            for i in range(9):
                y = top + 18 + i * 39
                x = left if side == 0 else right
                vx = 2.6 if side == 0 else -2.6
                vy = -1.8 if i < 4 else 1.8
                bullets.append(Bullet(
                    x, y, vx, vy, CYAN if side == 0 else PURPLE,
                    radius=6, ground=False,
                    ax=0.0, ay=(0.035 if i % 2 == 0 else -0.035)
                ))

    # 2. 일차함수: 기울기가 다른 직선 레인이 양쪽에서 교차
    elif p == 1:
        current_pattern_name = "일차함수 | 기울기 교차"
        for i in range(7):
            y = top + 25 + i * 48
            add_bullet(left, y, -0.20, 4.0, YELLOW, radius=6, ground=False)
            add_bullet(right, y, math.pi + 0.20, 4.0, CYAN, radius=6, ground=False)
        for i in range(5):
            x = left + 45 + i * 105
            add_bullet(x, top, math.pi / 2 + 0.35, 3.2, PURPLE, radius=5, ground=False)

    # 3. 원의 방정식: 경기장 중앙에서 두 겹의 원이 바깥으로 퍼짐
    elif p == 2:
        current_pattern_name = "원의 방정식 | 확장하는 동심원"
        cx, cy = ARENA.center
        for i in range(24):
            a = math.tau * i / 24
            add_bullet(cx, cy, a, 2.4, PURPLE, radius=6, ground=False)
        for i in range(16):
            a = math.tau * i / 16 + math.pi / 16
            add_bullet(cx, cy, a, 3.5, CYAN, radius=5, ground=False)

    # 4. 좌표와 거리: 네 꼭짓점과 변 중앙에서 추적탄 발사
    elif p == 3:
        current_pattern_name = "좌표와 거리 | 네 꼭짓점의 추적"
        points = [
            (left, top), (right, top), (left, bottom), (right, bottom),
            (ARENA.centerx, top), (ARENA.centerx, bottom),
        ]
        for i, (x, y) in enumerate(points):
            a = aim_angle(x, y, player.x, player.y)
            a += (-0.10 if i % 2 == 0 else 0.10)
            add_bullet(x, y, a, 3.0 + (i % 3) * 0.35,
                       CYAN if i % 2 == 0 else YELLOW, radius=7, ground=False)

    # 5. 점과 직선 사이의 거리: 평행선 모양의 탄막이 양쪽에서 진입
    elif p == 4:
        current_pattern_name = "점과 직선 사이의 거리 | 평행선 판결"
        for lane in range(5):
            y = top + 28 + lane * 68
            for j in range(4):
                yy = y + j * 7
                add_bullet(left, yy, -0.10, 4.2, RED, radius=5, ground=False)
                add_bullet(right, yy, math.pi + 0.10, 4.2, ORANGE, radius=5, ground=False)

    # 6. 명제: 무작위로 정해진 한 구역만 안전 통로
    elif p == 5:
        safe_lane = random.randrange(5)
        current_pattern_name = f"명제 | 참과 거짓 (안전 구역 {safe_lane + 1})"
        lane_width = ARENA.width / 5
        for lane in range(5):
            if lane == safe_lane:
                continue
            x0 = int(ARENA.left + lane * lane_width + 12)
            x1 = int(ARENA.left + (lane + 1) * lane_width - 12)
            for x in range(x0, x1, 24):
                add_bullet(x, top, math.pi / 2, random.uniform(3.2, 4.4),
                           GREEN if lane < safe_lane else RED, radius=5, ground=False)

    # 7. 산술·기하평균: 좌우의 속도 차이가 커지는 대칭 파동
    elif p == 6:
        current_pattern_name = "산술·기하평균 | 균형 붕괴"
        for i in range(8):
            y = top + 20 + i * 43
            speed = 2.4 + i * 0.22
            add_bullet(left, y, 0, speed, YELLOW, radius=6, ground=False)
            add_bullet(right, y, math.pi, 4.1 - i * 0.16, CYAN, radius=6, ground=False)
        for y in range(top, bottom, 32):
            add_bullet(ARENA.centerx, y, math.pi / 2, 2.8, WHITE, radius=4, ground=False)

    # 8. 합성함수: 위아래에서 진입해 서로 반대 방향으로 휘는 탄막
    else:
        current_pattern_name = "합성함수 | 휘어지는 차원의 파동"
        for i in range(11):
            x = left + 20 + i * 56
            direction = 1 if i % 2 == 0 else -1
            bullets.append(Bullet(
                x, top, direction * 0.45, 2.8,
                PURPLE if i % 2 == 0 else CYAN,
                radius=7, ground=False, ax=(-0.035 if i % 2 == 0 else 0.035)
            ))
            bullets.append(Bullet(
                x, bottom, -direction * 0.45, -2.8,
                YELLOW if i % 2 == 0 else RED,
                radius=7, ground=False, ax=(0.035 if i % 2 == 0 else -0.035)
            ))
    pattern_index = (pattern_index + 1) % 8


def start_logic_round():
    """원명제·역·이·대우를 섞어 내고, 색에 맞는 행동을 판정한다."""
    global logic_round_active, logic_round_timer, logic_form_index
    global logic_boss_blue, logic_should_attack, logic_feedback

    logic_form_index = random.randrange(len(logic_forms))
    logic_boss_blue = random.choice([True, False])

    # 판정 규칙: 원명제와 동치인 대우면 공격, 동치가 아닌 역·이면 공격 금지.
    # 기준 명제는 P→Q, 대우 ¬Q→¬P만 원명제와 항상 동치다.
    logic_should_attack = logic_form_index in (0, 3)

    logic_round_active = True
    logic_round_timer = 100  # 60 FPS 기준 약 1.7초
    logic_feedback = ""


def finish_logic_round(correct, message):
    global logic_round_active, logic_cooldown, logic_feedback, logic_feedback_timer
    logic_round_active = False
    logic_cooldown = 160
    logic_feedback = message if correct else "오답! HP -1"
    logic_feedback_timer = 55
    if correct:
        # 명제 문제를 맞히면 보스에게 추가 피해
        global boss_hp
        boss_hp -= 12
    else:
        global player
        if player.invincible <= 0:
            player.hp -= 1
            player.invincible = 75


def draw_laser():
    if laser_x is None:
        return

    if laser_timer > 18:
        # 발사 전 경고
        pygame.draw.line(
            screen, (255, 100, 100),
            (laser_x, ARENA.top),
            (laser_x, ARENA.bottom), 3
        )
    else:
        # 실제 레이저
        pygame.draw.line(
            screen, WHITE,
            (laser_x, ARENA.top),
            (laser_x, ARENA.bottom), 12
        )
        pygame.draw.line(
            screen, RED,
            (laser_x, ARENA.top),
            (laser_x, ARENA.bottom), 6
        )


# =========================
# 화면 그리기
# =========================
def draw_text(text, x, y, color=WHITE, font=FONT):
    image = font.render(text, True, color)
    screen.blit(image, (x, y))


def draw_arena():
    screen.fill(BLACK)

    # 배경 별
    for i in range(35):
        x = (i * 127 + 23) % W
        y = (i * 83 + 17) % H
        pygame.draw.circle(screen, (45, 40, 70),
                           (x, y), 1)

    pygame.draw.rect(screen, (20, 15, 35), ARENA)
    # 좌표평면 격자와 x/y축
    for gx in range(ARENA.left + 30, ARENA.right, 30):
        pygame.draw.line(screen, (32, 35, 65), (gx, ARENA.top), (gx, ARENA.bottom), 1)
    for gy in range(ARENA.top + 30, ARENA.bottom, 30):
        pygame.draw.line(screen, (32, 35, 65), (ARENA.left, gy), (ARENA.right, gy), 1)
    pygame.draw.line(screen, (65, 90, 130), (ARENA.left, ARENA.centery), (ARENA.right, ARENA.centery), 2)
    pygame.draw.line(screen, (65, 90, 130), (ARENA.centerx, ARENA.top), (ARENA.centerx, ARENA.bottom), 2)
    pygame.draw.rect(screen, WHITE, ARENA, 3)

    # 보스
    boss = BOSSES[boss_index]
    pulse = math.sin(frame * 0.06) * 4
    bx, by = 400, 85

    # 현재 문제에서 P(보스가 파란색)의 참/거짓을 색으로 표시한다.
    display_boss_color = (80, 230, 255) if logic_boss_blue else (255, 110, 45)
    pygame.draw.circle(
        screen, display_boss_color,
        (bx, by), int(25 + pulse)
    )
    pygame.draw.circle(
        screen, WHITE, (bx - 8, by - 3), 5
    )
    pygame.draw.circle(
        screen, WHITE, (bx + 8, by - 3), 5
    )
    pygame.draw.circle(
        screen, BLACK, (bx - 8, by - 3), 2
    )
    pygame.draw.circle(
        screen, BLACK, (bx + 8, by - 3), 2
    )

    draw_text(f"{boss['name']}  -  FINAL EXAM", 100, 12)
    draw_text("π", bx - 48, by - 27, PURPLE, BIG)
    draw_text("√x", bx + 28, by - 28, YELLOW, FONT)

    # 보스 오른쪽에 명제 카드 표시
    panel = pygame.Rect(465, 42, 325, 91)
    pygame.draw.rect(screen, (27, 25, 48), panel, border_radius=8)
    pygame.draw.rect(screen, YELLOW if logic_round_active else (90, 85, 125), panel, 2, border_radius=8)
    form_name, statement = logic_forms[logic_form_index]
    draw_text("기준: 파란색이면 공격", 475, 47, CYAN, SMALL_FONT)
    draw_text(f"판정: {form_name}", 475, 65, YELLOW, LOGIC_FONT)
    if statement == "보스가 파란색이 아니면 공격하지 않는다":
        draw_text("보스가 파란색이 아니면", 475, 87, WHITE, SMALL_FONT)
        draw_text("공격하지 않는다", 475, 105, WHITE, SMALL_FONT)
    elif statement == "공격하지 않으면 보스가 파란색이 아니다":
        draw_text("공격하지 않으면 보스가", 475, 87, WHITE, SMALL_FONT)
        draw_text("파란색이 아니다", 475, 105, WHITE, SMALL_FONT)
    else:
        draw_text(statement, 475, 89, WHITE, SMALL_FONT)
    if logic_round_active:
        draw_text("동치면 Z / 아니면 대기", 625, 111, CYAN, SMALL_FONT)
        draw_text(f"{logic_round_timer // 60 + 1}s", 750, 47, WHITE, SMALL_FONT)
    elif logic_feedback_timer > 0:
        draw_text(logic_feedback, 625, 111, GREEN if "정답" in logic_feedback else RED, SMALL_FONT)

    # 보스 체력
    pygame.draw.rect(screen, (65, 30, 45),
                     (100, 43, 600, 16))
    pygame.draw.rect(
        screen, boss["color"],
        (100, 43, max(0, int(600 * boss_hp / boss_max_hp)), 16)
    )

    # 플레이어 체력
    draw_text("HP", 100, 70, RED)
    for i in range(5):
        c = RED if i < player.hp else (65, 35, 45)
        pygame.draw.rect(screen, c,
                         (140 + i * 27, 75, 20, 10))

    draw_text(f"패턴 {pattern_index + 1}/8", 570, 70, YELLOW)
    draw_text(current_pattern_name, 100, 112, CYAN)


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

                if event.key == pygame.K_z:
                    if logic_round_active:
                        if logic_should_attack:
                            finish_logic_round(True, "정답! 공격 성공")
                        else:
                            finish_logic_round(False, "")
                    elif player.shoot_cooldown <= 0:
                        shots.append(
                            Shot(player.x, player.y - player.jump)
                        )
                        player.shoot_cooldown = 12

            elif event.key == pygame.K_RETURN:
                # 엔딩 또는 게임 오버 후 재시작
                player = Player()
                bullets.clear()
                shots.clear()
                boss_index = 0  # 유일한 보스: 수학의 지배자
                boss_hp = BOSSES[boss_index]["hp"]
                boss_max_hp = boss_hp
                pattern_timer = 0
                pattern_index = 0
                current_pattern_name = "준비"
                laser_x = None
                laser_timer = 0
                logic_round_active = False
                logic_round_timer = 0
                logic_cooldown = 120
                logic_form_index = 0
                logic_boss_blue = True
                logic_should_attack = True
                logic_feedback = ""
                logic_feedback_timer = 0
                game_state = "playing"

    if game_state == "playing":
        keys = pygame.key.get_pressed()
        player.update(keys)

        # 명제 퀴즈 라운드: Z를 눌러야 할지 참을지 판단
        if logic_feedback_timer > 0:
            logic_feedback_timer -= 1
        if logic_round_active:
            logic_round_timer -= 1
            if logic_round_timer <= 0:
                if logic_should_attack:
                    finish_logic_round(False, "")
                else:
                    finish_logic_round(True, "정답! 공격 금지 성공")
        else:
            logic_cooldown -= 1
            if logic_cooldown <= 0:
                start_logic_round()

        # 일정 시간마다 다음 공격
        pattern_timer += 1
        interval = max(70, int(150 / BOSSES[boss_index]["speed"]))

        if pattern_timer >= interval:
            pattern_timer = 0
            spawn_pattern()

        # 레이저 시간 갱신
        if laser_timer > 0:
            laser_timer -= 1

        if laser_timer <= 0:
            laser_x = None

        # 플레이어 탄환 이동 및 보스 공격
        for shot in shots[:]:
            shot.update()

            if shot.y < 0:
                shots.remove(shot)
                continue

            if math.hypot(shot.x - 400, shot.y - 85) < 32:
                shots.remove(shot)
                boss_hp -= 4

        # 보스 처치
        if boss_hp <= 0:
            game_state = "win"

        # 탄막 이동과 충돌 판정
        for bullet in bullets[:]:
            bullet.update()

            if not bullet.alive():
                bullets.remove(bullet)
                continue

            # 점프 중이면 지상 탄막은 회피한다.
            if bullet.ground and player.jump_time > 0:
                continue

            # 공중 탄환은 점프만으로 피할 수 없다.
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
                        game_state = "lose"

        # 레이저 충돌
        if (
            laser_x is not None
            and laser_timer <= 18
            and abs(player.x - laser_x) < 10
        ):
            if player.invincible <= 0:
                player.hp -= 1
                player.invincible = 75

                if player.hp <= 0:
                    game_state = "lose"

    # =========================
    # 렌더링
    # =========================
    draw_arena()

    draw_laser()

    for bullet in bullets:
        bullet.draw()

    for shot in shots:
        shot.draw()

    player.draw()

    draw_text(
        "이동: 방향키/WASD   점프: SPACE   공격: Z | 명제 퀴즈: 동치면 Z, 아니면 대기",
        90, 550, CYAN
    )

    if game_state == "win":
        screen.fill(BLACK)
        draw_text("FINAL EXAM CLEARED!",
                  155, 210, YELLOW, BIG)
        draw_text("수학의 지배자를 물리쳤다!", 255, 280)
        draw_text("ENTER: 다시 시작   ESC: 종료",
                  220, 350, WHITE)

    elif game_state == "lose":
        screen.fill(BLACK)
        draw_text("GAME OVER", 290, 220, RED, BIG)
        draw_text("점프 타이밍을 다시 연습해 봐!",
                  220, 285, WHITE)
        draw_text("ENTER: 다시 도전   ESC: 종료",
                  220, 350, WHITE)

    pygame.display.flip()

pygame.quit()