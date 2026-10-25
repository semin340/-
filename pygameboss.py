import math
import random
import pygame

pygame.init()

# =========================
# 기본 설정 (1920 x 1080 비율)
# =========================
W, H = 1920, 1080
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("SOUL JUMP - 수학 보스")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("malgungothic", 26)
BIG = pygame.font.SysFont("malgungothic", 54, bold=True)
LOGIC_FONT = pygame.font.SysFont("malgungothic", 22, bold=True)
SMALL_FONT = pygame.font.SysFont("malgungothic", 17)

BLACK = (10, 8, 20)
WHITE = (245, 245, 255)
RED = (255, 65, 95)
CYAN = (80, 230, 255)
PURPLE = (175, 90, 255)
YELLOW = (255, 220, 80)
ORANGE = (255, 110, 45)
GREEN = (100, 255, 150)

# 1920x1080 화면 크기에 맞춘 아레나 크기 (중앙 배치)
ARENA = pygame.Rect(310, 240, 1300, 700)

BOSSES = [
    {
        "name": "수학의 지배자",
        "color": (80, 230, 255),
        "hp": 300,
        "speed": 1.2,
    },
]

# =========================
# 게임 객체
# =========================
class Player:
    def __init__(self):
        self.x = 960 
        self.y = 650
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

        self.x += dx * speed
        self.y += dy * speed

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
            self.jump = math.sin(t * math.pi) * 70
        else:
            self.jump = 0

    def do_jump(self):
        if self.jump_cooldown <= 0 and self.jump_time <= 0:
            self.jump_time = 32
            self.jump_cooldown = 45

    def draw(self):
        pygame.draw.ellipse(
            screen, (65, 55, 80),
            (self.x - 16, self.y - 6, 32, 14)
        )

        draw_y = int(self.y - self.jump)

        if self.invincible > 0 and (self.invincible // 4) % 2 == 0:
            return

        points = [
            (self.x, draw_y - 18),
            (self.x + 18, draw_y - 3),
            (self.x + 13, draw_y + 13),
            (self.x, draw_y + 20),
            (self.x - 13, draw_y + 13),
            (self.x - 18, draw_y - 3),
        ]
        pygame.draw.polygon(screen, RED, points)
        pygame.draw.circle(screen, WHITE, (self.x - 4, draw_y - 2), 3)
        pygame.draw.circle(screen, WHITE, (self.x + 4, draw_y - 2), 3)


class Bullet:
    def __init__(self, x, y, vx, vy, color, radius=8, life=400):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.color = color
        self.r = radius
        self.life = life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(screen, WHITE, (int(self.x - 2), int(self.y - 2)), max(2, self.r // 3))

    def alive(self):
        return (
            self.life > 0
            and -50 < self.x < W + 50
            and -50 < self.y < H + 50
        )


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
        if not self.active:
            return
        self.elapsed += 1
        self.x += self.vx
        self.y = self.start_y + math.sin(self.elapsed * self.freq) * self.amp

        if self.x > ARENA.right - 90:
            self.vx = -3.0
        elif self.x < ARENA.left + 90:
            self.vx = 3.0

    def draw(self):
        if not self.active:
            return
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
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            bullets_list.append(Bullet(self.x, self.y, vx, vy, PURPLE, radius=8, life=250))
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

# =========================
# 전투 시스템 초기화
# =========================
player = Player()
giant_bullet = GiantWaveBullet(ARENA.left + 90, 0)
factor_bullets = []
circle_hazards = []
bullets = []
shots = []

boss_index = 0
boss_hp = BOSSES[boss_index]["hp"]
boss_max_hp = boss_hp

frame = 0
boss_shoot_timer = 0
circle_spawn_timer = 0
factor_spawn_timer = 0
boss_dialogue = ["", 0]
current_pattern_name = "종합 패턴: 웨이브 + 저격 + 원 + 인수분해"
game_state = "playing"

# 최종 시험 (사분면 패턴) 상태 변수
final_exam_active = False
final_exam_step = 0
final_exam_timer = 180
target_quadrant = 1
exam_phase = "waiting"

# 명제 퀴즈 상태 변수들
logic_forms = [
    ("보스가 파란색이라면 공격한다"),
    ("보스가 빨간색이라면 공격한다"),
    ("보스가 파란색이 아니라면 공격한다"),
    ("보스가 빨간색이 아니라면 공격한다"),
    ("보스가 파란색이라면 공격하지 않는다"),
    ("보스가 빨간색이라면 공격하지 않는다"),
]
logic_round_active = False
logic_form_index = 0
logic_boss_blue = True
logic_should_attack = True
logic_feedback = ""
logic_feedback_timer = 0

LOGIC_DURATION = 300
logic_timer = LOGIC_DURATION
logic_failed_state = False

def start_logic_round(is_phase2):
    global logic_round_active, logic_form_index
    global logic_boss_blue, logic_should_attack, logic_feedback, logic_timer

    logic_form_index = random.randrange(len(logic_forms))
    logic_boss_blue = random.choice([True, False])
    statement = logic_forms[logic_form_index]

    if "파란색이라면" in statement and "공격하지 않는다" not in statement:
        condition_true = logic_boss_blue
    elif "빨간색이라면" in statement and "공격하지 않는다" not in statement:
        condition_true = not logic_boss_blue
    elif "파란색이 아니라면" in statement:
        condition_true = not logic_boss_blue
    else:
        condition_true = logic_boss_blue

    if "공격하지 않는다" in statement:
        if "파란색이라면" in statement:
            logic_should_attack = not logic_boss_blue
        else:
            logic_should_attack = logic_boss_blue
    else:
        logic_should_attack = condition_true

    logic_round_active = True
    logic_timer = 180 if is_phase2 else 300
    logic_feedback = ""

def finish_logic_round(correct, message):
    global logic_feedback, logic_feedback_timer, logic_failed_state
    logic_feedback = message if correct else "오답! 공격 명중 시 보스 체력 회복"
    logic_feedback_timer = 120
    
    if correct:
        logic_failed_state = False
    else:
        logic_failed_state = True

# =========================
# 화면 그리기
# =========================
def draw_text(text, x, y, color=WHITE, font=FONT):
    image = font.render(text, True, color)
    screen.blit(image, (x, y))

def draw_arena():
    screen.fill(BLACK)

    for i in range(50):
        x = (i * 173 + 41) % W
        y = (i * 97 + 29) % H
        pygame.draw.circle(screen, (45, 40, 70), (x, y), 1)

    pygame.draw.rect(screen, (20, 15, 35), ARENA)
    
    for gx in range(ARENA.left + 50, ARENA.right, 50):
        pygame.draw.line(screen, (32, 35, 65), (gx, ARENA.top), (gx, ARENA.bottom), 1)
    for gy in range(ARENA.top + 50, ARENA.bottom, 50):
        pygame.draw.line(screen, (32, 35, 65), (ARENA.left, gy), (ARENA.right, gy), 1)
    
    # 최종 시험 중일 때 (때리는 checking 단계일 때만 빨간색 음영 칠하기)
    if final_exam_active:
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

    boss = BOSSES[boss_index]
    pulse = math.sin(frame * 0.06) * 6
    bx, by = ARENA.centerx, ARENA.top - 60

    if final_exam_active:
        display_boss_color = YELLOW
    else:
        display_boss_color = (80, 230, 255) if logic_boss_blue else (255, 110, 45)

    pygame.draw.circle(screen, display_boss_color, (bx, by), int(35 + pulse))
    pygame.draw.circle(screen, WHITE, (bx - 12, by - 5), 7)
    pygame.draw.circle(screen, WHITE, (bx + 12, by - 5), 7)
    pygame.draw.circle(screen, BLACK, (bx - 12, by - 5), 3)
    pygame.draw.circle(screen, BLACK, (bx + 12, by - 5), 3)

    if boss_dialogue[1] > 0:
        diag_surf = BIG.render(boss_dialogue[0], True, YELLOW if final_exam_active else GREEN)
        screen.blit(diag_surf, (bx - diag_surf.get_width() // 2, by - 110))

    draw_text(f"{boss['name']} - FINAL EXAM", ARENA.left, ARENA.top - 140, WHITE, BIG)
    draw_text("π", bx - 65, by - 38, PURPLE, BIG)
    draw_text("√x", bx + 35, by - 38, YELLOW, FONT)

    panel = pygame.Rect(ARENA.right - 520, ARENA.top - 135, 520, 100)
    pygame.draw.rect(screen, (27, 25, 48), panel, border_radius=10)
    pygame.draw.rect(screen, YELLOW if logic_round_active else (90, 85, 125), panel, 2, border_radius=10)
    
    statement = logic_forms[logic_form_index]
    draw_text(statement, panel.x + 20, panel.y + 35, YELLOW, LOGIC_FONT)

    seconds_left = max(0, logic_timer // 60 + 1)
    draw_text(f"{seconds_left}s", panel.x + 465, panel.y + 35, WHITE, SMALL_FONT)

    if logic_feedback_timer > 0:
        draw_text(logic_feedback, panel.x + 20, panel.y + 70, GREEN if "정답" in logic_feedback else RED, SMALL_FONT)

    pygame.draw.rect(screen, (65, 30, 45), (ARENA.left, ARENA.top - 45, ARENA.width, 22))
    pygame.draw.rect(screen, boss["color"], (ARENA.left, ARENA.top - 45, max(0, int(ARENA.width * boss_hp / boss_max_hp)), 22))

    draw_text("HP", ARENA.left, ARENA.bottom + 20, RED)
    for i in range(5):
        c = RED if i < player.hp else (65, 35, 45)
        pygame.draw.rect(screen, c, (ARENA.left + 50 + i * 35, ARENA.bottom + 23, 25, 16))

    if final_exam_active:
        status_msg = f"최종 시험 진행 중 ({final_exam_step}/4) - 안전한 구역으로 대피하세요!"
        draw_text(status_msg, ARENA.right - 650, ARENA.bottom + 20, YELLOW)
    else:
        phase_text = " [PHASE 2: 광폭화!]" if boss_hp <= boss_max_hp / 2 else ""
        draw_text(current_pattern_name + phase_text, ARENA.right - 550, ARENA.bottom + 20, RED if boss_hp <= boss_max_hp / 2 else CYAN)

# =========================
# 메인 게임 루프
# =========================
running = True
start_logic_round(False)

while running:
    clock.tick(60)
    frame += 1

    if boss_dialogue[1] > 0:
        boss_dialogue[1] -= 1

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
                    if logic_round_active and not final_exam_active:
                        if logic_should_attack:
                            finish_logic_round(True, "정답! 공격 준비 완료")
                        else:
                            finish_logic_round(False, "오답! 보스 회복 모드")
                    
                    if player.shoot_cooldown <= 0 and not final_exam_active:
                        shots.append(Shot(player.x, player.y - player.jump))
                        player.shoot_cooldown = 10

            elif event.key == pygame.K_RETURN:
                player = Player()
                giant_bullet = GiantWaveBullet(ARENA.left + 90, 0)
                factor_bullets.clear()
                circle_hazards.clear()
                bullets.clear()
                shots.clear()
                boss_hp = BOSSES[boss_index]["hp"]
                boss_max_hp = boss_hp
                logic_failed_state = False
                final_exam_active = False
                final_exam_step = 0
                exam_phase = "waiting"
                game_state = "playing"
                start_logic_round(False)

    if game_state == "playing":
        keys = pygame.key.get_pressed()
        player.update(keys)

        if boss_hp <= 0 and not final_exam_active:
            final_exam_active = True
            final_exam_step = 1
            exam_phase = "waiting"
            target_quadrant = random.randint(1, 4)
            final_exam_timer = 180  # 맨 처음만 3초 대기
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
                    final_exam_timer = 60  # 1초 동안 쾅! 때리면서 빨간색 칠하기 및 판정
                    boss_dialogue[0] = "쾅!"
                    boss_dialogue[1] = 60
            elif exam_phase == "checking":
                if final_exam_timer <= 0:
                    px, py = player.x, player.y
                    cx, cy = ARENA.centerx, ARENA.centery
                    
                    in_target = False
                    if target_quadrant == 1 and px >= cx and py <= cy:
                        in_target = True
                    elif target_quadrant == 2 and px <= cx and py <= cy:
                        in_target = True
                    elif target_quadrant == 3 and px <= cx and py >= cy:
                        in_target = True
                    elif target_quadrant == 4 and px >= cx and py >= cy:
                        in_target = True

                    if not in_target:
                        if player.invincible <= 0:
                            player.hp -= 1
                            player.invincible = 60
                            if player.hp <= 0:
                                game_state = "lose"

                    final_exam_step += 1
                    if final_exam_step > 4:
                        game_state = "win"
                    else:
                        exam_phase = "waiting"
                        target_quadrant = random.randint(1, 4)
                        final_exam_timer = 90  # 그 다음부터는 1.5초
                        boss_dialogue[0] = f"제{target_quadrant}사분면!"
                        boss_dialogue[1] = 90

        else:
            is_phase2 = boss_hp <= boss_max_hp / 2
            speed_mult = 1.3 if is_phase2 else 1.0

            if logic_feedback_timer > 0:
                logic_feedback_timer -= 1

            if logic_round_active:
                logic_timer -= 1
                if logic_timer <= 0:
                    start_logic_round(is_phase2)

            giant_bullet.update()

            boss_shoot_timer += 1
            if boss_shoot_timer >= 60:
                boss_shoot_timer = 0
                bx, by = ARENA.centerx, ARENA.top - 60
                px, py = player.x, player.y - player.jump
                angle = math.atan2(py - by, px - bx)
                speed = 4.5 * speed_mult
                bullets.append(Bullet(bx, by, math.cos(angle) * speed, math.sin(angle) * speed, ORANGE, radius=10, life=300))

            factor_spawn_timer += 1
            if factor_spawn_timer >= 210:
                factor_spawn_timer = 0
                bx, by = ARENA.centerx, ARENA.top - 60
                px, py = player.x, player.y - player.jump
                base_angle = math.atan2(py - by, px - bx)
                speed = 3.5 * speed_mult
                for spread in [-0.25, 0.0, 0.25]:
                    angle = base_angle + spread
                    factor_bullets.append(FactorBullet(bx, by, math.cos(angle) * speed, math.sin(angle) * speed))

            for fb in factor_bullets[:]:
                if fb.update(bullets, boss_dialogue, speed_mult):
                    factor_bullets.remove(fb)

            circle_spawn_timer += 1
            spawn_interval = 100 if is_phase2 else 150
            if circle_spawn_timer >= spawn_interval:
                circle_spawn_timer = 0
                ch = CirclePatternHazard()
                circle_hazards.append(ch)
                if is_phase2:
                    mirrored_x = 2 * ARENA.centerx - ch.x
                    mirrored_y = 2 * ARENA.centery - ch.y
                    circle_hazards.append(CirclePatternHazard(mirrored_x, mirrored_y))

            for ch in circle_hazards[:]:
                ch.update(bullets, speed_mult)
                if ch.exploded:
                    circle_hazards.remove(ch)

            if player.jump == 0:
                for bullet in bullets[:]:
                    bullet.update()
                    if not bullet.alive():
                        bullets.remove(bullet)
                        continue

                    distance = math.hypot(
                        bullet.x - player.x,
                        bullet.y - player.y
                    )
                    if distance < bullet.r + player.r:
                        bullets.remove(bullet)
                        if player.invincible <= 0:
                            player.hp -= 1
                            player.invincible = 60
                            if player.hp <= 0:
                                game_state = "lose"
            else:
                for bullet in bullets[:]:
                    bullet.update()
                    if not bullet.alive():
                        bullets.remove(bullet)

            for shot in shots[:]:
                shot.update()
                if shot.y < 0:
                    shots.remove(shot)
                    continue

                bx, by = ARENA.centerx, ARENA.top - 60
                if math.hypot(shot.x - bx, shot.y - by) < 40:
                    shots.remove(shot)
                    if logic_failed_state:
                        boss_hp = min(boss_max_hp, boss_hp + 20)
                        logic_failed_state = False
                    else:
                        boss_hp -= 10

            if boss_hp > boss_max_hp:
                boss_hp = boss_max_hp

            if player.jump == 0:
                distance = math.hypot(
                    giant_bullet.x - player.x,
                    giant_bullet.y - player.y
                )
                if distance < giant_bullet.r + player.r:
                    if player.invincible <= 0:
                        player.hp -= 1
                        player.invincible = 60

                        if player.hp <= 0:
                            game_state = "lose"

    draw_arena()

    for ch in circle_hazards:
        ch.draw()

    for fb in factor_bullets:
        fb.draw()

    for bullet in bullets:
        bullet.draw()

    giant_bullet.draw()

    for shot in shots:
        shot.draw()

    player.draw()

    draw_text("이동: 방향키/WASD    점프: SPACE (공중 무적!)    공격: Z", ARENA.left, ARENA.bottom + 70, CYAN)

    if game_state == "win":
        screen.fill(BLACK)
        draw_text("VICTORY!", W // 2 - 150, H // 2 - 80, YELLOW, BIG)
        draw_text("보스의 최종 시험을 완벽하게 돌파했습니다!", W // 2 - 240, H // 2, WHITE)
        draw_text("ENTER: 다시 시작    ESC: 종료", W // 2 - 180, H // 2 + 70, WHITE)

    elif game_state == "lose":
        screen.fill(BLACK)
        draw_text("GAME OVER", W // 2 - 170, H // 2 - 80, RED, BIG)
        draw_text("도전에 실패했습니다.", W // 2 - 120, H // 2, WHITE)
        draw_text("ENTER: 다시 도전    ESC: 종료", W // 2 - 180, H // 2 + 70, WHITE)

    pygame.display.flip()

pygame.quit()