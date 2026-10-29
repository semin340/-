import math
import random
import sys
import pygame

# =========================================================
# 한글 보스전 - Pygame (로비, 판정 완화, 피날레 3초 완결판)
# 조작: WASD 이동 / SPACE 점프 / ENTER 도전시작 / L 로비 / R 재시작 / ESC 종료
# =========================================================

pygame.init()

WIDTH = 1200
HEIGHT = 760
FPS = 60

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("한글 보스전: 국어의 시련 - 로비 및 밸런스 완결판")
CLOCK = pygame.time.Clock()

# ---------------------------------------------------------
# 색상
# ---------------------------------------------------------

BG = (39, 29, 30)
COVER = (70, 39, 34)
COVER_LIGHT = (111, 66, 47)
GOLD = (220, 177, 100)

PAPER = (246, 235, 207)
PAPER_LIGHT = (255, 249, 229)
PAPER_EDGE = (191, 161, 119)
PAPER_LINE = (216, 197, 160)

INK = (88, 54, 43)
RED = (213, 55, 51)
DARK_RED = (130, 34, 39)
GREEN = (49, 194, 104)
BLUE = (57, 112, 176)
WHITE = (255, 255, 255)

ARENA_LEFT = 105
ARENA_RIGHT = 1095
ARENA_TOP = 145
ARENA_BOTTOM = 610

PAGE_LINES = [330, 405, 480, 555]

PLAYER_SIZE = 30
PLAYER_SPEED = 340

JUMP_POWER = 600
GRAVITY = 1550

MAX_HP = 5

# ---------------------------------------------------------
# 폰트
# ---------------------------------------------------------

FONT_CACHE = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in FONT_CACHE:
        path = None
        for name in ["malgungothic", "nanumgothic", "gulim", "arial"]:
            path = pygame.font.match_font(name, bold=bold)
            if path:
                break
        if path:
            FONT_CACHE[key] = pygame.font.Font(path, size)
        else:
            FONT_CACHE[key] = pygame.font.Font(None, size)
    return FONT_CACHE[key]


def text(surface, message, size, color, center, bold=False):
    image = font(size, bold).render(message, True, color)
    rect = image.get_rect(center=(int(center[0]), int(center[1])))
    surface.blit(image, rect)
    return rect


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


# =========================================================
# 배경: 두꺼운 책
# =========================================================

def draw_background(surface):
    surface.fill(BG)
    pygame.draw.ellipse(surface, (17, 13, 16), (45, 642, 1110, 90))
    pygame.draw.rect(surface, (32, 22, 23), (38, 52, 1124, 633), border_radius=24)
    pygame.draw.rect(surface, COVER, (42, 48, 1116, 628), border_radius=23)
    pygame.draw.rect(surface, COVER_LIGHT, (51, 57, 1098, 609), width=3, border_radius=20)
    pygame.draw.rect(surface, GOLD, (65, 71, 1070, 581), width=2, border_radius=15)

    for i in range(7):
        y = 624 + i * 5
        pygame.draw.line(surface, (180 + i * 2, 148 + i, 100 + i), (78, y), (1122, y), 2)

    pygame.draw.polygon(surface, PAPER_EDGE, [(76, 94), (590, 112), (590, 620), (76, 608)])
    pygame.draw.polygon(surface, PAPER_EDGE, [(610, 112), (1124, 94), (1124, 608), (610, 620)])
    pygame.draw.polygon(surface, PAPER, [(83, 98), (587, 116), (587, 614), (83, 603)])
    pygame.draw.polygon(surface, PAPER, [(613, 116), (1117, 98), (1117, 603), (613, 614)])
    pygame.draw.polygon(surface, PAPER_LIGHT, [(86, 103), (580, 121), (580, 151), (86, 139)])
    pygame.draw.polygon(surface, PAPER_LIGHT, [(620, 121), (1114, 103), (1114, 139), (620, 151)])
    pygame.draw.polygon(surface, (211, 191, 153), [(587, 112), (600, 121), (600, 617), (587, 614)])
    pygame.draw.polygon(surface, (225, 207, 170), [(600, 121), (613, 112), (613, 614), (600, 617)])
    pygame.draw.line(surface, (165, 131, 91), (600, 121), (600, 617), 2)

    for y in [160, 235, 310, 385, 460, 535]:
        pygame.draw.arc(surface, (222, 207, 174), (88, y, 495, 34), math.pi, math.tau, 1)
        pygame.draw.arc(surface, (222, 207, 174), (615, y, 495, 34), math.pi, math.tau, 1)

    text(surface, "KOREAN BOSS", 14, (153, 116, 75), (180, 119), True)
    text(surface, "국어의 시련", 16, (153, 116, 75), (1015, 119), True)

    pygame.draw.rect(surface, (239, 225, 193), (93, 145, 1014, 477), width=2, border_radius=8)

    for y in PAGE_LINES:
        pygame.draw.line(surface, PAPER_LINE, (125, y), (1075, y), 2)

    pygame.draw.line(surface, (168, 132, 87), (108, ARENA_BOTTOM + 13), (1092, ARENA_BOTTOM + 13), 3)


# =========================================================
# 플레이어
# =========================================================

def create_player():
    return {
        "x": 585.0,
        "y": 430.0,
        "z": 0.0,
        "vz": 0.0,
        "on_ground": True,
        "size": PLAYER_SIZE,
    }


def player_ground_rect(player):
    return pygame.Rect(int(player["x"]), int(player["y"]), PLAYER_SIZE, PLAYER_SIZE)


def player_visual_rect(player):
    return pygame.Rect(int(player["x"]), int(player["y"] - player["z"]), PLAYER_SIZE, PLAYER_SIZE)


def update_player(player, dt, keys):
    dx, dy = 0, 0
    if keys[pygame.K_a]: dx -= 1
    if keys[pygame.K_d]: dx += 1
    if keys[pygame.K_w]: dy -= 1
    if keys[pygame.K_s]: dy += 1

    if dx != 0 or dy != 0:
        length = math.sqrt(dx * dx + dy * dy)
        dx /= length
        dy /= length

    player["x"] += dx * PLAYER_SPEED * dt
    player["y"] += dy * PLAYER_SPEED * dt

    player["x"] = clamp(player["x"], ARENA_LEFT + 5, ARENA_RIGHT - PLAYER_SIZE - 5)
    player["y"] = clamp(player["y"], ARENA_TOP + 5, ARENA_BOTTOM - PLAYER_SIZE)

    player["z"] += player["vz"] * dt
    player["vz"] -= GRAVITY * dt

    if player["z"] <= 0:
        player["z"] = 0
        player["vz"] = 0
        player["on_ground"] = True


def jump_player(player):
    if player["on_ground"]:
        player["vz"] = JUMP_POWER
        player["on_ground"] = False


def draw_player(surface, player):
    ground = player_ground_rect(player)
    visual = player_visual_rect(player)

    shadow_width = max(12, int(29 - player["z"] * 0.025))
    pygame.draw.ellipse(surface, (190, 169, 130), (ground.centerx - shadow_width, ground.bottom - 2, shadow_width * 2, 9))

    pygame.draw.rect(surface, BLUE, visual, border_radius=4)
    pygame.draw.rect(surface, (30, 54, 91), visual, width=3, border_radius=4)
    pygame.draw.line(surface, (119, 169, 220), (visual.left + 5, visual.top + 5), (visual.right - 5, visual.top + 5), 2)


# =========================================================
# 보스
# =========================================================

def draw_boss(surface, elapsed):
    x = WIDTH // 2
    y = 228 + int(math.sin(elapsed * 2.5) * 3)

    pygame.draw.ellipse(surface, (198, 177, 140), (x - 87, y + 47, 174, 23))
    pygame.draw.rect(surface, COVER, (x - 76, y - 40, 152, 90), border_radius=8)
    pygame.draw.rect(surface, PAPER_LIGHT, (x - 67, y - 43, 134, 81), border_radius=5)
    pygame.draw.line(surface, (190, 153, 106), (x, y - 39), (x, y + 35), 3)
    pygame.draw.rect(surface, GOLD, (x - 59, y - 32, 118, 60), width=2, border_radius=5)
    text(surface, "국어의왕", 27, (119, 44, 39), (x, y - 2), True)


# =========================================================
# 게임 상태 관리
# =========================================================

def new_game():
    return {
        "state": "lobby",
        "hp": MAX_HP,
        "elapsed": 0.0,
        "stage_timer": 0.0,
        "invincible": 0.0,
        "flash": 0.0,
        "shake": 0.0,
        "player": create_player(),
        "stage": "page1_p1",
        
        "warning_banner_timer": 0.0,
        
        # 패턴 1
        "bullets": [],
        "bullet_timer": 0.0,
        "bullet_index": 0,
        
        # 패턴 2
        "sentences": [],
        "sent_state": "warning",
        "sent_timer": 0.0,
        "sent_count": 0,
        "sent_cycle_state": "active",
        
        # 패턴 3
        "book_state": "warning",
        "book_timer": 0.0,
        "safe_rect": pygame.Rect(0, 0, 0, 0),
        "safe_success": False,
        
        # 패턴 4
        "grammar_phase": 0,
        "grammar_timer": 0.0,
        "grammar_choices": [],
        "grammar_wrong_side": None,
        "grammar_feedback_timer": 0.0,
        "remaining_quizzes": [],

        # 피날레 하드 모드
        "hard_book_state": "warning",
        "hard_book_timer": 0.0,
        "hard_safe_rect": pygame.Rect(0, 0, 0, 0),
        "hard_safe_success": False,
        "hard_book_count": 0,
    }


game = new_game()


def damage_player():
    if game["state"] != "playing":
        return
    if game["invincible"] > 0:
        return

    game["hp"] -= 1
    game["invincible"] = 0.7
    game["flash"] = 0.20
    game["shake"] = 0.25

    if game["hp"] <= 0:
        game["hp"] = 0
        game["state"] = "dead"


# =========================================================
# 패턴 1: 가나다라 탄환
# =========================================================

def update_pattern1(dt, speed_mul=1.0, scale=1.0):
    game["bullet_timer"] += dt
    interval = max(0.18, 0.60 - game["stage_timer"] * 0.02) / speed_mul

    while game["bullet_timer"] >= interval:
        game["bullet_timer"] -= interval
        player = game["player"]

        start_x = random.randint(ARENA_LEFT + 40, ARENA_RIGHT - 40)
        start_y = ARENA_TOP + 15
        
        letters = ["가", "나", "다", "라", "마", "바", "사"]
        idx = game["bullet_index"] % len(letters)
        letter = letters[idx]
        game["bullet_index"] += 1

        size = int((32 + idx * 3) * scale)
        vy = (280 + idx * 20) * speed_mul

        target_x = player["x"] + PLAYER_SIZE / 2
        vx = clamp((target_x - start_x) * 0.35, -200, 200)

        game["bullets"].append({
            "x": float(start_x), "y": float(start_y),
            "vx": vx, "vy": vy,
            "size": size, "letter": letter,
        })

    ground_rect = player_ground_rect(game["player"]).inflate(-4, -4)
    is_jumping = game["player"]["z"] > 5

    for bullet in game["bullets"][:]:
        bullet["x"] += bullet["vx"] * dt
        bullet["y"] += bullet["vy"] * dt
        rect = pygame.Rect(int(bullet["x"]), int(bullet["y"]), bullet["size"], bullet["size"])

        if rect.top > HEIGHT:
            game["bullets"].remove(bullet)
            continue

        if not is_jumping and rect.colliderect(ground_rect):
            damage_player()
            game["bullets"].remove(bullet)


def draw_bullets(surface):
    for bullet in game["bullets"]:
        rect = pygame.Rect(int(bullet["x"]), int(bullet["y"]), bullet["size"], bullet["size"])
        pygame.draw.rect(surface, (255, 240, 180), rect, border_radius=6)
        pygame.draw.rect(surface, RED, rect, width=2, border_radius=6)
        text(surface, bullet["letter"], int(bullet["size"] * 0.65), DARK_RED, rect.center, True)


# =========================================================
# 패턴 2: 문장 압박
# =========================================================

SENTENCES_POOL = ["국어의왕", "문학비독서", "맞춤법파괴", "고전문법시련", "비문학지옥"]

def start_pattern2(scale=1.0):
    game["sent_state"] = "warning"
    game["sent_timer"] = 0.0
    game["sent_cycle_state"] = "active"
    game["sentences"] = []

    max_attempts = 100
    for _ in range(4):
        for _ in range(max_attempts):
            is_vertical = random.choice([True, False])
            text_str = random.choice(SENTENCES_POOL)
            
            if is_vertical:
                w = int(75 * scale)
                h = int(240 * scale)
                rx = random.randint(ARENA_LEFT + 30, ARENA_RIGHT - w - 30)
                ry = random.randint(ARENA_TOP + 20, ARENA_BOTTOM - h - 20)
            else:
                w = int(300 * scale)
                h = int(70 * scale)
                rx = random.randint(ARENA_LEFT + 20, ARENA_RIGHT - w - 20)
                ry = random.randint(ARENA_TOP + 30, ARENA_BOTTOM - h - 30)

            candidate_rect = pygame.Rect(rx, ry, w, h)
            
            overlap = False
            for s in game["sentences"]:
                if candidate_rect.inflate(15, 15).colliderect(s["rect"]):
                    overlap = True
                    break
            
            if not overlap:
                game["sentences"].append({
                    "text": text_str,
                    "rect": candidate_rect,
                    "vertical": is_vertical,
                    "scale": scale
                })
                break


def update_pattern2(dt, speed_mul=1.0, scale=1.0):
    game["sent_timer"] += dt

    if game["sent_cycle_state"] == "active":
        warn_duration = 0.5 / speed_mul
        active_duration = 1.3 / speed_mul

        if game["sent_state"] == "warning":
            if game["sent_timer"] >= warn_duration:
                game["sent_state"] = "active"
                game["sent_timer"] = 0.0

        elif game["sent_state"] == "active":
            ground_rect = player_ground_rect(game["player"]).inflate(-4, -4)
            is_jumping = game["player"]["z"] > 5

            if not is_jumping:
                for s in game["sentences"]:
                    if s["rect"].colliderect(ground_rect):
                        damage_player()

            if game["sent_timer"] >= active_duration:
                game["sentences"].clear()
                game["sent_cycle_state"] = "resting"
                game["sent_timer"] = 0.0

    elif game["sent_cycle_state"] == "resting":
        if game["sent_timer"] >= 0.6:
            game["sent_count"] += 1
            if game["sent_count"] >= 6:
                game["sent_count"] = 0
                return True
            else:
                start_pattern2(scale=scale)
    return False


def draw_pattern2(surface):
    if game["sent_cycle_state"] == "resting":
        return

    for s in game["sentences"]:
        rect = s["rect"]
        scale = s.get("scale", 1.0)
        
        if game["sent_state"] == "warning":
            blink_phase = (int(game["sent_timer"] * 20) % 2) == 0
            if blink_phase:
                color = (255, 40, 30)
                bg_color = (255, 200, 190)
            else:
                color = (190, 20, 10)
                bg_color = (240, 160, 150)

            pygame.draw.rect(surface, bg_color, rect, border_radius=8)
            pygame.draw.rect(surface, color, rect, width=int(4 * scale), border_radius=8)
            text(surface, "경고!", int(24 * scale), color, rect.center, True)

        elif game["sent_state"] == "active":
            pygame.draw.rect(surface, (130, 25, 20), rect, border_radius=8)
            pygame.draw.rect(surface, (255, 225, 165), rect, width=int(4 * scale), border_radius=8)
            text(surface, s["text"], int(26 * scale), WHITE, rect.center, True)


# =========================================================
# 패턴 3: 세로 책 덮기
# =========================================================

def start_pattern3():
    safe_width = 110
    safe_height = 230
    safe_x = random.randint(ARENA_LEFT + 80, ARENA_RIGHT - safe_width - 80)
    safe_y = random.randint(ARENA_TOP + 40, ARENA_BOTTOM - safe_height - 40)

    game["safe_rect"] = pygame.Rect(safe_x, safe_y, safe_width, safe_height)
    game["book_state"] = "warning"
    game["book_timer"] = 0.0
    game["safe_success"] = False


def update_pattern3(dt):
    game["book_timer"] += dt
    state = game["book_state"]
    warn_time = 2.0
    close_time = 0.65
    open_time = 0.6

    if state == "warning":
        if game["book_timer"] >= warn_time:
            game["book_state"] = "closing"
            game["book_timer"] = 0.0

    elif state == "closing":
        player = game["player"]
        safe = game["safe_rect"]
        p_center = (player["x"] + PLAYER_SIZE / 2, player["y"] + PLAYER_SIZE / 2)

        inside = safe.collidepoint(int(p_center[0]), int(p_center[1]))
        jumping = player["z"] > 5
        game["safe_success"] = inside and jumping

        if game["book_timer"] >= close_time:
            if not game["safe_success"]:
                damage_player()
            game["book_state"] = "reopening"
            game["book_timer"] = 0.0

    elif state == "reopening":
        if game["book_timer"] >= open_time:
            return True
    return False


def draw_book_vertical(surface, progress):
    progress = clamp(progress, 0.0, 1.0)
    cover_width = int(500 * progress)

    if cover_width > 0:
        left_cover = pygame.Rect(ARENA_LEFT, ARENA_TOP, cover_width, ARENA_BOTTOM - ARENA_TOP)
        right_cover = pygame.Rect(ARENA_RIGHT - cover_width, ARENA_TOP, cover_width, ARENA_BOTTOM - ARENA_TOP)
        pygame.draw.rect(surface, (221, 200, 159), left_cover)
        pygame.draw.rect(surface, (196, 170, 126), right_cover)

    if progress > 0.72:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alpha = int((progress - 0.72) / 0.28 * 150)
        overlay.fill((23, 13, 14, alpha))
        surface.blit(overlay, (0, 0))


def draw_pattern3_ui(surface):
    safe = game["safe_rect"]
    state = game["book_state"]

    if state == "warning":
        pulse = (math.sin(game["book_timer"] * 15) + 1) / 2
        color = (40, 160 + int(80 * pulse), 85)
        pygame.draw.rect(surface, color, safe, width=4, border_radius=8)
        text(surface, "SAFE", 18, GREEN, (safe.centerx, safe.top - 17), True)
        text(surface, "초록 원 안에서 책이 덮힐 때 점프하라!", 23, RED, (WIDTH // 2, 282), True)

    elif state == "closing":
        progress = game["book_timer"] / 0.65
        draw_book_vertical(surface, progress)

    elif state == "reopening":
        progress = 1.0 - game["book_timer"] / 0.6
        draw_book_vertical(surface, progress)


# =========================================================
# 패턴 4: 맞춤법 퀴즈
# =========================================================

ALL_GRAMMAR_QUIZZES = [
    ("금세", "금새", True),
    ("안돼요", "안되요", True),
    ("설거지", "설겆이", True),
    ("몇일", "며칠", False),
    ("띄어쓰기", "띄여쓰기", True),
]

def start_grammar_quiz():
    if not game["remaining_quizzes"]:
        game["remaining_quizzes"] = list(ALL_GRAMMAR_QUIZZES)
        random.shuffle(game["remaining_quizzes"])

    q1, q2, left_is_correct = game["remaining_quizzes"].pop()
    game["grammar_timer"] = 0.0
    game["grammar_feedback_timer"] = 0.0
    game["grammar_wrong_side"] = None

    if random.choice([True, False]):
        if left_is_correct:
            game["grammar_choices"] = [(q1, True), (q2, False)]
        else:
            game["grammar_choices"] = [(q2, False), (q1, True)]
    else:
        if left_is_correct:
            game["grammar_choices"] = [(q2, False), (q1, True)]
        else:
            game["grammar_choices"] = [(q1, True), (q2, False)]


def update_grammar_quiz(dt):
    if game["grammar_wrong_side"] is not None:
        game["grammar_feedback_timer"] += dt
        if game["grammar_feedback_timer"] >= 5.0:
            game["grammar_wrong_side"] = None
            game["grammar_phase"] += 1
            if game["grammar_phase"] >= 4:
                game["grammar_phase"] = 0
                return True
            else:
                start_grammar_quiz()
        return False

    game["grammar_timer"] += dt
    if game["grammar_timer"] >= 6.0:
        player = game["player"]
        p_x = player["x"] + PLAYER_SIZE / 2
        p_y = player["y"] + PLAYER_SIZE / 2
        
        left_rect = pygame.Rect(ARENA_LEFT + 35, ARENA_TOP + 85, 380, 280)
        right_rect = pygame.Rect(ARENA_RIGHT - 415, ARENA_TOP + 85, 380, 280)
        
        in_left = left_rect.collidepoint(int(p_x), int(p_y))
        in_right = right_rect.collidepoint(int(p_x), int(p_y))
        
        if not in_left and not in_right:
            mid_x = (ARENA_LEFT + ARENA_RIGHT) / 2
            chosen_left = p_x < mid_x
        else:
            chosen_left = in_left
        
        left_correct = game["grammar_choices"][0][1]
        player_chose_correct = (chosen_left and left_correct) or (not chosen_left and not left_correct)
        
        if not player_chose_correct:
            damage_player()
            game["grammar_wrong_side"] = "left" if chosen_left else "right"
            game["grammar_feedback_timer"] = 0.0
        else:
            game["grammar_phase"] += 1
            if game["grammar_phase"] >= 4:
                game["grammar_phase"] = 0
                return True
            else:
                start_grammar_quiz()
    return False


def draw_grammar_quiz(surface):
    left_rect = pygame.Rect(ARENA_LEFT + 50, ARENA_TOP + 100, 350, 250)
    right_rect = pygame.Rect(ARENA_RIGHT - 400, ARENA_TOP + 100, 350, 250)

    if game["grammar_wrong_side"] == "left":
        pygame.draw.rect(surface, (15, 10, 14), left_rect, border_radius=12)
        text(surface, "전체 뜯김!", 35, RED, left_rect.center, True)
    else:
        pygame.draw.rect(surface, (255, 248, 230), left_rect, border_radius=12)
        pygame.draw.rect(surface, BLUE, left_rect, width=3, border_radius=12)
        text(surface, game["grammar_choices"][0][0], 42, INK, left_rect.center, True)

    if game["grammar_wrong_side"] == "right":
        pygame.draw.rect(surface, (15, 10, 14), right_rect, border_radius=12)
        text(surface, "전체 뜯김!", 35, RED, right_rect.center, True)
    else:
        pygame.draw.rect(surface, (255, 248, 230), right_rect, border_radius=12)
        pygame.draw.rect(surface, RED, right_rect, width=3, border_radius=12)
        text(surface, game["grammar_choices"][1][0], 42, INK, right_rect.center, True)

    remaining_sec = max(0.0, 6.0 - game["grammar_timer"])
    if game["grammar_wrong_side"] is not None:
        text(surface, "틀렸다! 오답 구역 전체가 뜯겨나갔다!", 25, RED, (WIDTH // 2, 200), True)
    else:
        text(surface, f"올바른 맞춤법 구역에서 대기/점프! 남은 시간: {remaining_sec:03.1f}초 (총 4문제)", 21, DARK_RED, (WIDTH // 2, 200), True)


# =========================================================
# 피날레 하드 모드 책 덮기
# =========================================================

def start_hard_book():
    safe_width = 80
    safe_height = 160
    safe_x = random.randint(ARENA_LEFT + 100, ARENA_RIGHT - safe_width - 100)
    safe_y = random.randint(ARENA_TOP + 50, ARENA_BOTTOM - safe_height - 50)

    game["hard_safe_rect"] = pygame.Rect(safe_x, safe_y, safe_width, safe_height)
    game["hard_book_state"] = "warning"
    game["hard_book_timer"] = 0.0
    game["hard_safe_success"] = False


def update_hard_book(dt):
    game["hard_book_timer"] += dt
    state = game["hard_book_state"]
    warn_time = 3.0
    close_time = 0.45
    open_time = 0.5

    if state == "warning":
        if game["hard_book_timer"] >= warn_time:
            game["hard_book_state"] = "closing"
            game["hard_book_timer"] = 0.0

    elif state == "closing":
        player = game["player"]
        safe = game["hard_safe_rect"]
        p_center = (player["x"] + PLAYER_SIZE / 2, player["y"] + PLAYER_SIZE / 2)

        inside = safe.collidepoint(int(p_center[0]), int(p_center[1]))
        jumping = player["z"] > 5
        game["hard_safe_success"] = inside and jumping

        if game["hard_book_timer"] >= close_time:
            if not game["hard_safe_success"]:
                damage_player()
            game["hard_book_state"] = "reopening"
            game["hard_book_timer"] = 0.0

    elif state == "reopening":
        if game["hard_book_timer"] >= open_time:
            game["hard_book_count"] += 1
            if game["hard_book_count"] >= 4:
                return True
            else:
                start_hard_book()
    return False


def draw_hard_book_ui(surface):
    safe = game["hard_safe_rect"]
    state = game["hard_book_state"]

    if state == "warning":
        pulse = (math.sin(game["hard_book_timer"] * 25) + 1) / 2
        color = (40, 160 + int(80 * pulse), 85)
        pygame.draw.rect(surface, color, safe, width=4, border_radius=8)
        text(surface, f"HARD SAFE ({game['hard_book_count']+1}/4)", 16, GREEN, (safe.centerx, safe.top - 17), True)
        text(surface, "최종 피날레! 초소형 원 안에서 3초 내로 들어가 점프하라!", 22, RED, (WIDTH // 2, 282), True)

    elif state == "closing":
        progress = game["hard_book_timer"] / 0.45
        draw_book_vertical(surface, progress)

    elif state == "reopening":
        progress = 1.0 - game["hard_book_timer"] / 0.5
        draw_book_vertical(surface, progress)


# =========================================================
# 메인 게임 루프 및 업데이트
# =========================================================

def update_game(dt, keys):
    if game["state"] != "playing":
        return

    if game["warning_banner_timer"] > 0:
        game["warning_banner_timer"] -= dt

    game["elapsed"] += dt
    game["stage_timer"] += dt

    if game["invincible"] > 0:
        game["invincible"] = max(0.0, game["invincible"] - dt)
    if game["flash"] > 0:
        game["flash"] = max(0.0, game["flash"] - dt)
    if game["shake"] > 0:
        game["shake"] = max(0.0, game["shake"] - dt)

    update_player(game["player"], dt, keys)

    # 스테이지 진행 흐름
    if game["stage"] == "page1_p1":
        update_pattern1(dt, speed_mul=1.0, scale=1.0)
        if game["stage_timer"] >= 10.0:
            game["stage"] = "page1_p2"
            game["stage_timer"] = 0.0
            game["sent_count"] = 0
            start_pattern2(scale=1.0)

    elif game["stage"] == "page1_p2":
        if update_pattern2(dt, speed_mul=1.0, scale=1.0):
            game["stage"] = "page1_p3"
            game["stage_timer"] = 0.0
            start_pattern3()

    elif game["stage"] == "page1_p3":
        if update_pattern3(dt):
            game["stage"] = "page2_mix"
            game["stage_timer"] = 0.0
            game["warning_banner_timer"] = 2.5
            game["bullets"].clear()
            game["sent_count"] = 0
            start_pattern2(scale=1.3)

    elif game["stage"] == "page2_mix":
        update_pattern1(dt, speed_mul=1.3, scale=1.3)
        if update_pattern2(dt, speed_mul=1.3, scale=1.3):
            game["stage"] = "page2_grammar"
            game["stage_timer"] = 0.0
            game["sentences"].clear()
            start_grammar_quiz()

    elif game["stage"] == "page2_grammar":
        update_pattern1(dt, speed_mul=1.3, scale=1.3)
        if update_grammar_quiz(dt):
            game["stage"] = "final_hard_book"
            game["stage_timer"] = 0.0
            game["bullets"].clear()
            start_hard_book()

    elif game["stage"] == "final_hard_book":
        update_pattern1(dt, speed_mul=1.4, scale=1.3)
        if update_hard_book(dt):
            game["state"] = "clear"


def render():
    world = pygame.Surface((WIDTH, HEIGHT))

    draw_background(world)
    draw_boss(world, game["elapsed"])
    draw_hud(world)

    if game["stage"] in ["page1_p2", "page2_mix"]:
        draw_pattern2(world)

    if game["stage"] == "page1_p3":
        draw_pattern3_ui(world)

    if game["stage"] == "page2_grammar":
        draw_grammar_quiz(world)

    if game["stage"] == "final_hard_book":
        draw_hard_book_ui(world)

    if game["stage"] in ["page1_p1", "page2_mix", "page2_grammar", "final_hard_book"]:
        draw_bullets(world)

    player = game["player"]
    if game["invincible"] <= 0 or int(game["invincible"] * 12) % 2 == 0:
        draw_player(world, player)

    if "page2" in game["stage"] or game["stage"] == "final_hard_book":
        pulse_alpha = int(25 + 20 * math.sin(pygame.time.get_ticks() * 0.01))
        flash_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        flash_overlay.fill((200, 30, 20, pulse_alpha))
        world.blit(flash_overlay, (0, 0))

    SCREEN.blit(world, (0, 0))

    if game["warning_banner_timer"] > 0:
        banner_surf = pygame.Surface((WIDTH, 90), pygame.SRCALPHA)
        banner_surf.fill((15, 10, 12, 210))
        SCREEN.blit(banner_surf, (0, HEIGHT // 2 - 45))
        pygame.draw.line(SCREEN, RED, (0, HEIGHT // 2 - 45), (WIDTH, HEIGHT // 2 - 45), 3)
        pygame.draw.line(SCREEN, RED, (0, HEIGHT // 2 + 45), (WIDTH, HEIGHT // 2 + 45), 3)
        text(SCREEN, "경고: 2페이지 진입 - 더 혹독한 시련이 시작됩니다!", 28, WHITE, (WIDTH // 2, HEIGHT // 2), True)

    if game["flash"] > 0:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 30, 30, 60))
        SCREEN.blit(overlay, (0, 0))

    if game["state"] == "lobby":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((25, 18, 22, 240))
        SCREEN.blit(overlay, (0, 0))

        pygame.draw.rect(SCREEN, GOLD, (WIDTH // 2 - 380, HEIGHT // 2 - 210, 760, 400), width=4, border_radius=18)
        
        text(SCREEN, "한글 보스전: 국어의 시련", 54, GOLD, (WIDTH // 2, HEIGHT // 2 - 120), True)
        text(SCREEN, "국어의 모든 시련을 이겨내고 마스터가 되어라!", 22, WHITE, (WIDTH // 2, HEIGHT // 2 - 50), True)
        
        btn_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 10, 320, 65)
        pygame.draw.rect(SCREEN, (213, 55, 51), btn_rect, border_radius=12)
        pygame.draw.rect(SCREEN, GOLD, btn_rect, width=2, border_radius=12)
        text(SCREEN, "〈 국어 시련 도전하기 〉", 24, WHITE, btn_rect.center, True)
        
        text(SCREEN, "ENTER 키를 누르거나 버튼을 누르면 시작합니다", 18, (220, 210, 201), (WIDTH // 2, HEIGHT // 2 + 115))

    elif game["state"] == "dead":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((18, 11, 15, 195))
        SCREEN.blit(overlay, (0, 0))
        text(SCREEN, "GAME OVER", 70, (255, 75, 73), (WIDTH // 2, HEIGHT // 2 - 60), True)
        text(SCREEN, "R 키: 다시 시작", 24, WHITE, (WIDTH // 2, HEIGHT // 2 + 15))
        text(SCREEN, "L 키: 로비로 돌아가기", 22, GOLD, (WIDTH // 2, HEIGHT // 2 + 55))
        text(SCREEN, "ESC 키: 게임 종료", 18, (220, 210, 201), (WIDTH // 2, HEIGHT // 2 + 95))

    elif game["state"] == "clear":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 12, 25, 225))
        SCREEN.blit(overlay, (0, 0))

        pygame.draw.rect(SCREEN, GOLD, (WIDTH // 2 - 350, HEIGHT // 2 - 190, 700, 340), width=4, border_radius=16)
        
        text(SCREEN, "★ VICTORY! ★", 72, GOLD, (WIDTH // 2, HEIGHT // 2 - 110), True)
        text(SCREEN, "국어의 모든 시련과 피날레를 완벽하게 돌파했다!", 23, WHITE, (WIDTH // 2, HEIGHT // 2 - 30), True)
        text(SCREEN, "당신은 진정한 국어의 마스터입니다!", 21, (255, 230, 150), (WIDTH // 2, HEIGHT // 2 + 12), True)
        
        text(SCREEN, "R 키: 다시 플레이", 21, (242, 223, 183), (WIDTH // 2, HEIGHT // 2 + 75))
        text(SCREEN, "L 키: 로비로 돌아가기", 21, GOLD, (WIDTH // 2, HEIGHT // 2 + 115))

    pygame.display.flip()


def draw_hud(surface):
    text(surface, "PLAYER HP", 17, INK, (155, 170), True)

    for i in range(MAX_HP):
        rect = pygame.Rect(105 + i * 38, 188, 29, 18)
        color = RED if i < game["hp"] else (206, 190, 157)
        pygame.draw.rect(surface, color, rect, border_radius=4)

    page_str = "FINAL" if game["stage"] == "final_hard_book" else ("PAGE 2" if "page2" in game["stage"] else "PAGE 1")
    text(surface, f"{page_str}", 18, INK, (1020, 169), True)

    stage_names = {
        "page1_p1": "1페이지: 가나다라 탄막",
        "page1_p2": "1페이지: 문장 압박 (6회)",
        "page1_p3": "1페이지: 세로 책 덮기",
        "page2_mix": "2페이지: 거대해진 혼합 탄막 (6회)",
        "page2_grammar": "2페이지: 맞춤법 선택 퀴즈 (4문제)",
        "final_hard_book": "피날레: 하드 모드 책 덮기 (4연속)"
    }

    draw_panel = pygame.Rect(405, 157, 390, 33)
    pygame.draw.rect(surface, (255, 247, 223), draw_panel, border_radius=8)
    pygame.draw.rect(surface, (205, 176, 127), draw_panel, width=2, border_radius=8)
    text(surface, stage_names.get(game["stage"], ""), 17, INK, draw_panel.center, True)
    text(surface, "WASD 이동     SPACE 점프     L 로비로", 16, (112, 81, 53), (WIDTH // 2, 690))


def main():
    running = True
    while running:
        dt = min(CLOCK.tick(FPS) / 1000.0, 0.025)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and game["state"] == "lobby":
                btn_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 10, 320, 65)
                if btn_rect.collidepoint(event.pos):
                    game.clear()
                    game.update(new_game())
                    game["state"] = "playing"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN:
                    if game["state"] == "lobby":
                        game.clear()
                        game.update(new_game())
                        game["state"] = "playing"
                elif event.key == pygame.K_SPACE:
                    if game["state"] == "playing":
                        jump_player(game["player"])
                elif event.key == pygame.K_r:
                    if game["state"] in ("dead", "clear"):
                        game.clear()
                        game.update(new_game())
                        game["state"] = "playing"
                elif event.key == pygame.K_l:
                    if game["state"] in ("playing", "dead", "clear"):
                        game.clear()
                        game.update(new_game())
                        game["state"] = "lobby"

        keys = pygame.key.get_pressed()
        update_game(dt, keys)
        render()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()