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

# =========================
# 국어 보스 게임 (별도 네임스페이스로 통합)
# =========================
import types
_korean_source = 'import math\nimport random\nimport sys\nimport pygame\n\n# =========================================================\n# 한글 보스전 - Pygame (로비, 판정 완화, 피날레 3초 완결판)\n# 조작: WASD 이동 / SPACE 점프 / ENTER 도전시작 / L 로비 / R 재시작 / ESC 종료\n# =========================================================\n\npygame.init()\n\nWIDTH = 1200\nHEIGHT = 760\nFPS = 60\n\nSCREEN = pygame.Surface((WIDTH, HEIGHT))\npygame.display.set_caption("한글 보스전: 국어의 시련 - 로비 및 밸런스 완결판")\nCLOCK = pygame.time.Clock()\n\n# ---------------------------------------------------------\n# 색상\n# ---------------------------------------------------------\n\nBG = (39, 29, 30)\nCOVER = (70, 39, 34)\nCOVER_LIGHT = (111, 66, 47)\nGOLD = (220, 177, 100)\n\nPAPER = (246, 235, 207)\nPAPER_LIGHT = (255, 249, 229)\nPAPER_EDGE = (191, 161, 119)\nPAPER_LINE = (216, 197, 160)\n\nINK = (88, 54, 43)\nRED = (213, 55, 51)\nDARK_RED = (130, 34, 39)\nGREEN = (49, 194, 104)\nBLUE = (57, 112, 176)\nWHITE = (255, 255, 255)\n\nARENA_LEFT = 105\nARENA_RIGHT = 1095\nARENA_TOP = 145\nARENA_BOTTOM = 610\n\nPAGE_LINES = [330, 405, 480, 555]\n\nPLAYER_SIZE = 30\nPLAYER_SPEED = 340\n\nJUMP_POWER = 600\nGRAVITY = 1550\n\nMAX_HP = 5\n\n# ---------------------------------------------------------\n# 폰트\n# ---------------------------------------------------------\n\nFONT_CACHE = {}\n\n\ndef font(size, bold=False):\n    key = (size, bold)\n    if key not in FONT_CACHE:\n        path = None\n        for name in ["malgungothic", "nanumgothic", "gulim", "arial"]:\n            path = pygame.font.match_font(name, bold=bold)\n            if path:\n                break\n        if path:\n            FONT_CACHE[key] = pygame.font.Font(path, size)\n        else:\n            FONT_CACHE[key] = pygame.font.Font(None, size)\n    return FONT_CACHE[key]\n\n\ndef text(surface, message, size, color, center, bold=False):\n    image = font(size, bold).render(message, True, color)\n    rect = image.get_rect(center=(int(center[0]), int(center[1])))\n    surface.blit(image, rect)\n    return rect\n\n\ndef clamp(value, minimum, maximum):\n    return max(minimum, min(value, maximum))\n\n\n# =========================================================\n# 배경: 두꺼운 책\n# =========================================================\n\ndef draw_background(surface):\n    surface.fill(BG)\n    pygame.draw.ellipse(surface, (17, 13, 16), (45, 642, 1110, 90))\n    pygame.draw.rect(surface, (32, 22, 23), (38, 52, 1124, 633), border_radius=24)\n    pygame.draw.rect(surface, COVER, (42, 48, 1116, 628), border_radius=23)\n    pygame.draw.rect(surface, COVER_LIGHT, (51, 57, 1098, 609), width=3, border_radius=20)\n    pygame.draw.rect(surface, GOLD, (65, 71, 1070, 581), width=2, border_radius=15)\n\n    for i in range(7):\n        y = 624 + i * 5\n        pygame.draw.line(surface, (180 + i * 2, 148 + i, 100 + i), (78, y), (1122, y), 2)\n\n    pygame.draw.polygon(surface, PAPER_EDGE, [(76, 94), (590, 112), (590, 620), (76, 608)])\n    pygame.draw.polygon(surface, PAPER_EDGE, [(610, 112), (1124, 94), (1124, 608), (610, 620)])\n    pygame.draw.polygon(surface, PAPER, [(83, 98), (587, 116), (587, 614), (83, 603)])\n    pygame.draw.polygon(surface, PAPER, [(613, 116), (1117, 98), (1117, 603), (613, 614)])\n    pygame.draw.polygon(surface, PAPER_LIGHT, [(86, 103), (580, 121), (580, 151), (86, 139)])\n    pygame.draw.polygon(surface, PAPER_LIGHT, [(620, 121), (1114, 103), (1114, 139), (620, 151)])\n    pygame.draw.polygon(surface, (211, 191, 153), [(587, 112), (600, 121), (600, 617), (587, 614)])\n    pygame.draw.polygon(surface, (225, 207, 170), [(600, 121), (613, 112), (613, 614), (600, 617)])\n    pygame.draw.line(surface, (165, 131, 91), (600, 121), (600, 617), 2)\n\n    for y in [160, 235, 310, 385, 460, 535]:\n        pygame.draw.arc(surface, (222, 207, 174), (88, y, 495, 34), math.pi, math.tau, 1)\n        pygame.draw.arc(surface, (222, 207, 174), (615, y, 495, 34), math.pi, math.tau, 1)\n\n    text(surface, "KOREAN BOSS", 14, (153, 116, 75), (180, 119), True)\n    text(surface, "국어의 시련", 16, (153, 116, 75), (1015, 119), True)\n\n    pygame.draw.rect(surface, (239, 225, 193), (93, 145, 1014, 477), width=2, border_radius=8)\n\n    for y in PAGE_LINES:\n        pygame.draw.line(surface, PAPER_LINE, (125, y), (1075, y), 2)\n\n    pygame.draw.line(surface, (168, 132, 87), (108, ARENA_BOTTOM + 13), (1092, ARENA_BOTTOM + 13), 3)\n\n\n# =========================================================\n# 플레이어\n# =========================================================\n\ndef create_player():\n    return {\n        "x": 585.0,\n        "y": 430.0,\n        "z": 0.0,\n        "vz": 0.0,\n        "on_ground": True,\n        "size": PLAYER_SIZE,\n    }\n\n\ndef player_ground_rect(player):\n    return pygame.Rect(int(player["x"]), int(player["y"]), PLAYER_SIZE, PLAYER_SIZE)\n\n\ndef player_visual_rect(player):\n    return pygame.Rect(int(player["x"]), int(player["y"] - player["z"]), PLAYER_SIZE, PLAYER_SIZE)\n\n\ndef update_player(player, dt, keys):\n    dx, dy = 0, 0\n    if keys[pygame.K_a]: dx -= 1\n    if keys[pygame.K_d]: dx += 1\n    if keys[pygame.K_w]: dy -= 1\n    if keys[pygame.K_s]: dy += 1\n\n    if dx != 0 or dy != 0:\n        length = math.sqrt(dx * dx + dy * dy)\n        dx /= length\n        dy /= length\n\n    player["x"] += dx * PLAYER_SPEED * dt\n    player["y"] += dy * PLAYER_SPEED * dt\n\n    player["x"] = clamp(player["x"], ARENA_LEFT + 5, ARENA_RIGHT - PLAYER_SIZE - 5)\n    player["y"] = clamp(player["y"], ARENA_TOP + 5, ARENA_BOTTOM - PLAYER_SIZE)\n\n    player["z"] += player["vz"] * dt\n    player["vz"] -= GRAVITY * dt\n\n    if player["z"] <= 0:\n        player["z"] = 0\n        player["vz"] = 0\n        player["on_ground"] = True\n\n\ndef jump_player(player):\n    if player["on_ground"]:\n        player["vz"] = JUMP_POWER\n        player["on_ground"] = False\n\n\ndef draw_player(surface, player):\n    ground = player_ground_rect(player)\n    visual = player_visual_rect(player)\n\n    shadow_width = max(12, int(29 - player["z"] * 0.025))\n    pygame.draw.ellipse(surface, (190, 169, 130), (ground.centerx - shadow_width, ground.bottom - 2, shadow_width * 2, 9))\n\n    pygame.draw.rect(surface, BLUE, visual, border_radius=4)\n    pygame.draw.rect(surface, (30, 54, 91), visual, width=3, border_radius=4)\n    pygame.draw.line(surface, (119, 169, 220), (visual.left + 5, visual.top + 5), (visual.right - 5, visual.top + 5), 2)\n\n\n# =========================================================\n# 보스\n# =========================================================\n\ndef draw_boss(surface, elapsed):\n    x = WIDTH // 2\n    y = 228 + int(math.sin(elapsed * 2.5) * 3)\n\n    pygame.draw.ellipse(surface, (198, 177, 140), (x - 87, y + 47, 174, 23))\n    pygame.draw.rect(surface, COVER, (x - 76, y - 40, 152, 90), border_radius=8)\n    pygame.draw.rect(surface, PAPER_LIGHT, (x - 67, y - 43, 134, 81), border_radius=5)\n    pygame.draw.line(surface, (190, 153, 106), (x, y - 39), (x, y + 35), 3)\n    pygame.draw.rect(surface, GOLD, (x - 59, y - 32, 118, 60), width=2, border_radius=5)\n    text(surface, "국어의왕", 27, (119, 44, 39), (x, y - 2), True)\n\n\n# =========================================================\n# 게임 상태 관리\n# =========================================================\n\ndef new_game():\n    return {\n        "state": "lobby",\n        "hp": MAX_HP,\n        "elapsed": 0.0,\n        "stage_timer": 0.0,\n        "invincible": 0.0,\n        "flash": 0.0,\n        "shake": 0.0,\n        "player": create_player(),\n        "stage": "page1_p1",\n        \n        "warning_banner_timer": 0.0,\n        \n        # 패턴 1\n        "bullets": [],\n        "bullet_timer": 0.0,\n        "bullet_index": 0,\n        \n        # 패턴 2\n        "sentences": [],\n        "sent_state": "warning",\n        "sent_timer": 0.0,\n        "sent_count": 0,\n        "sent_cycle_state": "active",\n        \n        # 패턴 3\n        "book_state": "warning",\n        "book_timer": 0.0,\n        "safe_rect": pygame.Rect(0, 0, 0, 0),\n        "safe_success": False,\n        \n        # 패턴 4\n        "grammar_phase": 0,\n        "grammar_timer": 0.0,\n        "grammar_choices": [],\n        "grammar_wrong_side": None,\n        "grammar_feedback_timer": 0.0,\n        "remaining_quizzes": [],\n\n        # 피날레 하드 모드\n        "hard_book_state": "warning",\n        "hard_book_timer": 0.0,\n        "hard_safe_rect": pygame.Rect(0, 0, 0, 0),\n        "hard_safe_success": False,\n        "hard_book_count": 0,\n    }\n\n\ngame = new_game()\n\n\ndef damage_player():\n    if game["state"] != "playing":\n        return\n    if game["invincible"] > 0:\n        return\n\n    game["hp"] -= 1\n    game["invincible"] = 0.7\n    game["flash"] = 0.20\n    game["shake"] = 0.25\n\n    if game["hp"] <= 0:\n        game["hp"] = 0\n        game["state"] = "dead"\n\n\n# =========================================================\n# 패턴 1: 가나다라 탄환\n# =========================================================\n\ndef update_pattern1(dt, speed_mul=1.0, scale=1.0):\n    game["bullet_timer"] += dt\n    interval = max(0.18, 0.60 - game["stage_timer"] * 0.02) / speed_mul\n\n    while game["bullet_timer"] >= interval:\n        game["bullet_timer"] -= interval\n        player = game["player"]\n\n        start_x = random.randint(ARENA_LEFT + 40, ARENA_RIGHT - 40)\n        start_y = ARENA_TOP + 15\n        \n        letters = ["가", "나", "다", "라", "마", "바", "사"]\n        idx = game["bullet_index"] % len(letters)\n        letter = letters[idx]\n        game["bullet_index"] += 1\n\n        size = int((32 + idx * 3) * scale)\n        vy = (280 + idx * 20) * speed_mul\n\n        target_x = player["x"] + PLAYER_SIZE / 2\n        vx = clamp((target_x - start_x) * 0.35, -200, 200)\n\n        game["bullets"].append({\n            "x": float(start_x), "y": float(start_y),\n            "vx": vx, "vy": vy,\n            "size": size, "letter": letter,\n        })\n\n    ground_rect = player_ground_rect(game["player"]).inflate(-4, -4)\n    is_jumping = game["player"]["z"] > 5\n\n    for bullet in game["bullets"][:]:\n        bullet["x"] += bullet["vx"] * dt\n        bullet["y"] += bullet["vy"] * dt\n        rect = pygame.Rect(int(bullet["x"]), int(bullet["y"]), bullet["size"], bullet["size"])\n\n        if rect.top > HEIGHT:\n            game["bullets"].remove(bullet)\n            continue\n\n        if not is_jumping and rect.colliderect(ground_rect):\n            damage_player()\n            game["bullets"].remove(bullet)\n\n\ndef draw_bullets(surface):\n    for bullet in game["bullets"]:\n        rect = pygame.Rect(int(bullet["x"]), int(bullet["y"]), bullet["size"], bullet["size"])\n        pygame.draw.rect(surface, (255, 240, 180), rect, border_radius=6)\n        pygame.draw.rect(surface, RED, rect, width=2, border_radius=6)\n        text(surface, bullet["letter"], int(bullet["size"] * 0.65), DARK_RED, rect.center, True)\n\n\n# =========================================================\n# 패턴 2: 문장 압박\n# =========================================================\n\nSENTENCES_POOL = ["국어의왕", "문학비독서", "맞춤법파괴", "고전문법시련", "비문학지옥"]\n\ndef start_pattern2(scale=1.0):\n    game["sent_state"] = "warning"\n    game["sent_timer"] = 0.0\n    game["sent_cycle_state"] = "active"\n    game["sentences"] = []\n\n    max_attempts = 100\n    for _ in range(4):\n        for _ in range(max_attempts):\n            is_vertical = random.choice([True, False])\n            text_str = random.choice(SENTENCES_POOL)\n            \n            if is_vertical:\n                w = int(75 * scale)\n                h = int(240 * scale)\n                rx = random.randint(ARENA_LEFT + 30, ARENA_RIGHT - w - 30)\n                ry = random.randint(ARENA_TOP + 20, ARENA_BOTTOM - h - 20)\n            else:\n                w = int(300 * scale)\n                h = int(70 * scale)\n                rx = random.randint(ARENA_LEFT + 20, ARENA_RIGHT - w - 20)\n                ry = random.randint(ARENA_TOP + 30, ARENA_BOTTOM - h - 30)\n\n            candidate_rect = pygame.Rect(rx, ry, w, h)\n            \n            overlap = False\n            for s in game["sentences"]:\n                if candidate_rect.inflate(15, 15).colliderect(s["rect"]):\n                    overlap = True\n                    break\n            \n            if not overlap:\n                game["sentences"].append({\n                    "text": text_str,\n                    "rect": candidate_rect,\n                    "vertical": is_vertical,\n                    "scale": scale\n                })\n                break\n\n\ndef update_pattern2(dt, speed_mul=1.0, scale=1.0):\n    game["sent_timer"] += dt\n\n    if game["sent_cycle_state"] == "active":\n        warn_duration = 0.5 / speed_mul\n        active_duration = 1.3 / speed_mul\n\n        if game["sent_state"] == "warning":\n            if game["sent_timer"] >= warn_duration:\n                game["sent_state"] = "active"\n                game["sent_timer"] = 0.0\n\n        elif game["sent_state"] == "active":\n            ground_rect = player_ground_rect(game["player"]).inflate(-4, -4)\n            is_jumping = game["player"]["z"] > 5\n\n            if not is_jumping:\n                for s in game["sentences"]:\n                    if s["rect"].colliderect(ground_rect):\n                        damage_player()\n\n            if game["sent_timer"] >= active_duration:\n                game["sentences"].clear()\n                game["sent_cycle_state"] = "resting"\n                game["sent_timer"] = 0.0\n\n    elif game["sent_cycle_state"] == "resting":\n        if game["sent_timer"] >= 0.6:\n            game["sent_count"] += 1\n            if game["sent_count"] >= 6:\n                game["sent_count"] = 0\n                return True\n            else:\n                start_pattern2(scale=scale)\n    return False\n\n\ndef draw_pattern2(surface):\n    if game["sent_cycle_state"] == "resting":\n        return\n\n    for s in game["sentences"]:\n        rect = s["rect"]\n        scale = s.get("scale", 1.0)\n        \n        if game["sent_state"] == "warning":\n            blink_phase = (int(game["sent_timer"] * 20) % 2) == 0\n            if blink_phase:\n                color = (255, 40, 30)\n                bg_color = (255, 200, 190)\n            else:\n                color = (190, 20, 10)\n                bg_color = (240, 160, 150)\n\n            pygame.draw.rect(surface, bg_color, rect, border_radius=8)\n            pygame.draw.rect(surface, color, rect, width=int(4 * scale), border_radius=8)\n            text(surface, "경고!", int(24 * scale), color, rect.center, True)\n\n        elif game["sent_state"] == "active":\n            pygame.draw.rect(surface, (130, 25, 20), rect, border_radius=8)\n            pygame.draw.rect(surface, (255, 225, 165), rect, width=int(4 * scale), border_radius=8)\n            text(surface, s["text"], int(26 * scale), WHITE, rect.center, True)\n\n\n# =========================================================\n# 패턴 3: 세로 책 덮기\n# =========================================================\n\ndef start_pattern3():\n    safe_width = 110\n    safe_height = 230\n    safe_x = random.randint(ARENA_LEFT + 80, ARENA_RIGHT - safe_width - 80)\n    safe_y = random.randint(ARENA_TOP + 40, ARENA_BOTTOM - safe_height - 40)\n\n    game["safe_rect"] = pygame.Rect(safe_x, safe_y, safe_width, safe_height)\n    game["book_state"] = "warning"\n    game["book_timer"] = 0.0\n    game["safe_success"] = False\n\n\ndef update_pattern3(dt):\n    game["book_timer"] += dt\n    state = game["book_state"]\n    warn_time = 2.0\n    close_time = 0.65\n    open_time = 0.6\n\n    if state == "warning":\n        if game["book_timer"] >= warn_time:\n            game["book_state"] = "closing"\n            game["book_timer"] = 0.0\n\n    elif state == "closing":\n        player = game["player"]\n        safe = game["safe_rect"]\n        p_center = (player["x"] + PLAYER_SIZE / 2, player["y"] + PLAYER_SIZE / 2)\n\n        inside = safe.collidepoint(int(p_center[0]), int(p_center[1]))\n        jumping = player["z"] > 5\n        game["safe_success"] = inside and jumping\n\n        if game["book_timer"] >= close_time:\n            if not game["safe_success"]:\n                damage_player()\n            game["book_state"] = "reopening"\n            game["book_timer"] = 0.0\n\n    elif state == "reopening":\n        if game["book_timer"] >= open_time:\n            return True\n    return False\n\n\ndef draw_book_vertical(surface, progress):\n    progress = clamp(progress, 0.0, 1.0)\n    cover_width = int(500 * progress)\n\n    if cover_width > 0:\n        left_cover = pygame.Rect(ARENA_LEFT, ARENA_TOP, cover_width, ARENA_BOTTOM - ARENA_TOP)\n        right_cover = pygame.Rect(ARENA_RIGHT - cover_width, ARENA_TOP, cover_width, ARENA_BOTTOM - ARENA_TOP)\n        pygame.draw.rect(surface, (221, 200, 159), left_cover)\n        pygame.draw.rect(surface, (196, 170, 126), right_cover)\n\n    if progress > 0.72:\n        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)\n        alpha = int((progress - 0.72) / 0.28 * 150)\n        overlay.fill((23, 13, 14, alpha))\n        surface.blit(overlay, (0, 0))\n\n\ndef draw_pattern3_ui(surface):\n    safe = game["safe_rect"]\n    state = game["book_state"]\n\n    if state == "warning":\n        pulse = (math.sin(game["book_timer"] * 15) + 1) / 2\n        color = (40, 160 + int(80 * pulse), 85)\n        pygame.draw.rect(surface, color, safe, width=4, border_radius=8)\n        text(surface, "SAFE", 18, GREEN, (safe.centerx, safe.top - 17), True)\n        text(surface, "초록 원 안에서 책이 덮힐 때 점프하라!", 23, RED, (WIDTH // 2, 282), True)\n\n    elif state == "closing":\n        progress = game["book_timer"] / 0.65\n        draw_book_vertical(surface, progress)\n\n    elif state == "reopening":\n        progress = 1.0 - game["book_timer"] / 0.6\n        draw_book_vertical(surface, progress)\n\n\n# =========================================================\n# 패턴 4: 맞춤법 퀴즈\n# =========================================================\n\nALL_GRAMMAR_QUIZZES = [\n    ("금세", "금새", True),\n    ("안돼요", "안되요", True),\n    ("설거지", "설겆이", True),\n    ("몇일", "며칠", False),\n    ("띄어쓰기", "띄여쓰기", True),\n]\n\ndef start_grammar_quiz():\n    if not game["remaining_quizzes"]:\n        game["remaining_quizzes"] = list(ALL_GRAMMAR_QUIZZES)\n        random.shuffle(game["remaining_quizzes"])\n\n    q1, q2, left_is_correct = game["remaining_quizzes"].pop()\n    game["grammar_timer"] = 0.0\n    game["grammar_feedback_timer"] = 0.0\n    game["grammar_wrong_side"] = None\n\n    if random.choice([True, False]):\n        if left_is_correct:\n            game["grammar_choices"] = [(q1, True), (q2, False)]\n        else:\n            game["grammar_choices"] = [(q2, False), (q1, True)]\n    else:\n        if left_is_correct:\n            game["grammar_choices"] = [(q2, False), (q1, True)]\n        else:\n            game["grammar_choices"] = [(q1, True), (q2, False)]\n\n\ndef update_grammar_quiz(dt):\n    if game["grammar_wrong_side"] is not None:\n        game["grammar_feedback_timer"] += dt\n        if game["grammar_feedback_timer"] >= 5.0:\n            game["grammar_wrong_side"] = None\n            game["grammar_phase"] += 1\n            if game["grammar_phase"] >= 4:\n                game["grammar_phase"] = 0\n                return True\n            else:\n                start_grammar_quiz()\n        return False\n\n    game["grammar_timer"] += dt\n    if game["grammar_timer"] >= 6.0:\n        player = game["player"]\n        p_x = player["x"] + PLAYER_SIZE / 2\n        p_y = player["y"] + PLAYER_SIZE / 2\n        \n        left_rect = pygame.Rect(ARENA_LEFT + 35, ARENA_TOP + 85, 380, 280)\n        right_rect = pygame.Rect(ARENA_RIGHT - 415, ARENA_TOP + 85, 380, 280)\n        \n        in_left = left_rect.collidepoint(int(p_x), int(p_y))\n        in_right = right_rect.collidepoint(int(p_x), int(p_y))\n        \n        if not in_left and not in_right:\n            mid_x = (ARENA_LEFT + ARENA_RIGHT) / 2\n            chosen_left = p_x < mid_x\n        else:\n            chosen_left = in_left\n        \n        left_correct = game["grammar_choices"][0][1]\n        player_chose_correct = (chosen_left and left_correct) or (not chosen_left and not left_correct)\n        \n        if not player_chose_correct:\n            damage_player()\n            game["grammar_wrong_side"] = "left" if chosen_left else "right"\n            game["grammar_feedback_timer"] = 0.0\n        else:\n            game["grammar_phase"] += 1\n            if game["grammar_phase"] >= 4:\n                game["grammar_phase"] = 0\n                return True\n            else:\n                start_grammar_quiz()\n    return False\n\n\ndef draw_grammar_quiz(surface):\n    left_rect = pygame.Rect(ARENA_LEFT + 50, ARENA_TOP + 100, 350, 250)\n    right_rect = pygame.Rect(ARENA_RIGHT - 400, ARENA_TOP + 100, 350, 250)\n\n    if game["grammar_wrong_side"] == "left":\n        pygame.draw.rect(surface, (15, 10, 14), left_rect, border_radius=12)\n        text(surface, "전체 뜯김!", 35, RED, left_rect.center, True)\n    else:\n        pygame.draw.rect(surface, (255, 248, 230), left_rect, border_radius=12)\n        pygame.draw.rect(surface, BLUE, left_rect, width=3, border_radius=12)\n        text(surface, game["grammar_choices"][0][0], 42, INK, left_rect.center, True)\n\n    if game["grammar_wrong_side"] == "right":\n        pygame.draw.rect(surface, (15, 10, 14), right_rect, border_radius=12)\n        text(surface, "전체 뜯김!", 35, RED, right_rect.center, True)\n    else:\n        pygame.draw.rect(surface, (255, 248, 230), right_rect, border_radius=12)\n        pygame.draw.rect(surface, RED, right_rect, width=3, border_radius=12)\n        text(surface, game["grammar_choices"][1][0], 42, INK, right_rect.center, True)\n\n    remaining_sec = max(0.0, 6.0 - game["grammar_timer"])\n    if game["grammar_wrong_side"] is not None:\n        text(surface, "틀렸다! 오답 구역 전체가 뜯겨나갔다!", 25, RED, (WIDTH // 2, 200), True)\n    else:\n        text(surface, f"올바른 맞춤법 구역에서 대기/점프! 남은 시간: {remaining_sec:03.1f}초 (총 4문제)", 21, DARK_RED, (WIDTH // 2, 200), True)\n\n\n# =========================================================\n# 피날레 하드 모드 책 덮기\n# =========================================================\n\ndef start_hard_book():\n    safe_width = 80\n    safe_height = 160\n    safe_x = random.randint(ARENA_LEFT + 100, ARENA_RIGHT - safe_width - 100)\n    safe_y = random.randint(ARENA_TOP + 50, ARENA_BOTTOM - safe_height - 50)\n\n    game["hard_safe_rect"] = pygame.Rect(safe_x, safe_y, safe_width, safe_height)\n    game["hard_book_state"] = "warning"\n    game["hard_book_timer"] = 0.0\n    game["hard_safe_success"] = False\n\n\ndef update_hard_book(dt):\n    game["hard_book_timer"] += dt\n    state = game["hard_book_state"]\n    warn_time = 3.0\n    close_time = 0.45\n    open_time = 0.5\n\n    if state == "warning":\n        if game["hard_book_timer"] >= warn_time:\n            game["hard_book_state"] = "closing"\n            game["hard_book_timer"] = 0.0\n\n    elif state == "closing":\n        player = game["player"]\n        safe = game["hard_safe_rect"]\n        p_center = (player["x"] + PLAYER_SIZE / 2, player["y"] + PLAYER_SIZE / 2)\n\n        inside = safe.collidepoint(int(p_center[0]), int(p_center[1]))\n        jumping = player["z"] > 5\n        game["hard_safe_success"] = inside and jumping\n\n        if game["hard_book_timer"] >= close_time:\n            if not game["hard_safe_success"]:\n                damage_player()\n            game["hard_book_state"] = "reopening"\n            game["hard_book_timer"] = 0.0\n\n    elif state == "reopening":\n        if game["hard_book_timer"] >= open_time:\n            game["hard_book_count"] += 1\n            if game["hard_book_count"] >= 4:\n                return True\n            else:\n                start_hard_book()\n    return False\n\n\ndef draw_hard_book_ui(surface):\n    safe = game["hard_safe_rect"]\n    state = game["hard_book_state"]\n\n    if state == "warning":\n        pulse = (math.sin(game["hard_book_timer"] * 25) + 1) / 2\n        color = (40, 160 + int(80 * pulse), 85)\n        pygame.draw.rect(surface, color, safe, width=4, border_radius=8)\n        text(surface, f"HARD SAFE ({game[\'hard_book_count\']+1}/4)", 16, GREEN, (safe.centerx, safe.top - 17), True)\n        text(surface, "최종 피날레! 초소형 원 안에서 3초 내로 들어가 점프하라!", 22, RED, (WIDTH // 2, 282), True)\n\n    elif state == "closing":\n        progress = game["hard_book_timer"] / 0.45\n        draw_book_vertical(surface, progress)\n\n    elif state == "reopening":\n        progress = 1.0 - game["hard_book_timer"] / 0.5\n        draw_book_vertical(surface, progress)\n\n\n# =========================================================\n# 메인 게임 루프 및 업데이트\n# =========================================================\n\ndef update_game(dt, keys):\n    if game["state"] != "playing":\n        return\n\n    if game["warning_banner_timer"] > 0:\n        game["warning_banner_timer"] -= dt\n\n    game["elapsed"] += dt\n    game["stage_timer"] += dt\n\n    if game["invincible"] > 0:\n        game["invincible"] = max(0.0, game["invincible"] - dt)\n    if game["flash"] > 0:\n        game["flash"] = max(0.0, game["flash"] - dt)\n    if game["shake"] > 0:\n        game["shake"] = max(0.0, game["shake"] - dt)\n\n    update_player(game["player"], dt, keys)\n\n    # 스테이지 진행 흐름\n    if game["stage"] == "page1_p1":\n        update_pattern1(dt, speed_mul=1.0, scale=1.0)\n        if game["stage_timer"] >= 10.0:\n            game["stage"] = "page1_p2"\n            game["stage_timer"] = 0.0\n            game["sent_count"] = 0\n            start_pattern2(scale=1.0)\n\n    elif game["stage"] == "page1_p2":\n        if update_pattern2(dt, speed_mul=1.0, scale=1.0):\n            game["stage"] = "page1_p3"\n            game["stage_timer"] = 0.0\n            start_pattern3()\n\n    elif game["stage"] == "page1_p3":\n        if update_pattern3(dt):\n            game["stage"] = "page2_mix"\n            game["stage_timer"] = 0.0\n            game["warning_banner_timer"] = 2.5\n            game["bullets"].clear()\n            game["sent_count"] = 0\n            start_pattern2(scale=1.3)\n\n    elif game["stage"] == "page2_mix":\n        update_pattern1(dt, speed_mul=1.3, scale=1.3)\n        if update_pattern2(dt, speed_mul=1.3, scale=1.3):\n            game["stage"] = "page2_grammar"\n            game["stage_timer"] = 0.0\n            game["sentences"].clear()\n            start_grammar_quiz()\n\n    elif game["stage"] == "page2_grammar":\n        update_pattern1(dt, speed_mul=1.3, scale=1.3)\n        if update_grammar_quiz(dt):\n            game["stage"] = "final_hard_book"\n            game["stage_timer"] = 0.0\n            game["bullets"].clear()\n            start_hard_book()\n\n    elif game["stage"] == "final_hard_book":\n        update_pattern1(dt, speed_mul=1.4, scale=1.3)\n        if update_hard_book(dt):\n            game["state"] = "clear"\n\n\ndef render():\n    world = pygame.Surface((WIDTH, HEIGHT))\n\n    draw_background(world)\n    draw_boss(world, game["elapsed"])\n    draw_hud(world)\n\n    if game["stage"] in ["page1_p2", "page2_mix"]:\n        draw_pattern2(world)\n\n    if game["stage"] == "page1_p3":\n        draw_pattern3_ui(world)\n\n    if game["stage"] == "page2_grammar":\n        draw_grammar_quiz(world)\n\n    if game["stage"] == "final_hard_book":\n        draw_hard_book_ui(world)\n\n    if game["stage"] in ["page1_p1", "page2_mix", "page2_grammar", "final_hard_book"]:\n        draw_bullets(world)\n\n    player = game["player"]\n    if game["invincible"] <= 0 or int(game["invincible"] * 12) % 2 == 0:\n        draw_player(world, player)\n\n    if "page2" in game["stage"] or game["stage"] == "final_hard_book":\n        pulse_alpha = int(25 + 20 * math.sin(pygame.time.get_ticks() * 0.01))\n        flash_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)\n        flash_overlay.fill((200, 30, 20, pulse_alpha))\n        world.blit(flash_overlay, (0, 0))\n\n    SCREEN.blit(world, (0, 0))\n\n    if game["warning_banner_timer"] > 0:\n        banner_surf = pygame.Surface((WIDTH, 90), pygame.SRCALPHA)\n        banner_surf.fill((15, 10, 12, 210))\n        SCREEN.blit(banner_surf, (0, HEIGHT // 2 - 45))\n        pygame.draw.line(SCREEN, RED, (0, HEIGHT // 2 - 45), (WIDTH, HEIGHT // 2 - 45), 3)\n        pygame.draw.line(SCREEN, RED, (0, HEIGHT // 2 + 45), (WIDTH, HEIGHT // 2 + 45), 3)\n        text(SCREEN, "경고: 2페이지 진입 - 더 혹독한 시련이 시작됩니다!", 28, WHITE, (WIDTH // 2, HEIGHT // 2), True)\n\n    if game["flash"] > 0:\n        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)\n        overlay.fill((255, 30, 30, 60))\n        SCREEN.blit(overlay, (0, 0))\n\n    if game["state"] == "lobby":\n        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)\n        overlay.fill((25, 18, 22, 240))\n        SCREEN.blit(overlay, (0, 0))\n\n        pygame.draw.rect(SCREEN, GOLD, (WIDTH // 2 - 380, HEIGHT // 2 - 210, 760, 400), width=4, border_radius=18)\n        \n        text(SCREEN, "한글 보스전: 국어의 시련", 54, GOLD, (WIDTH // 2, HEIGHT // 2 - 120), True)\n        text(SCREEN, "국어의 모든 시련을 이겨내고 마스터가 되어라!", 22, WHITE, (WIDTH // 2, HEIGHT // 2 - 50), True)\n        \n        btn_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 10, 320, 65)\n        pygame.draw.rect(SCREEN, (213, 55, 51), btn_rect, border_radius=12)\n        pygame.draw.rect(SCREEN, GOLD, btn_rect, width=2, border_radius=12)\n        text(SCREEN, "〈 국어 시련 도전하기 〉", 24, WHITE, btn_rect.center, True)\n        \n        text(SCREEN, "ENTER 키를 누르거나 버튼을 누르면 시작합니다", 18, (220, 210, 201), (WIDTH // 2, HEIGHT // 2 + 115))\n\n    elif game["state"] == "dead":\n        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)\n        overlay.fill((18, 11, 15, 195))\n        SCREEN.blit(overlay, (0, 0))\n        text(SCREEN, "GAME OVER", 70, (255, 75, 73), (WIDTH // 2, HEIGHT // 2 - 60), True)\n        text(SCREEN, "R 키: 다시 시작", 24, WHITE, (WIDTH // 2, HEIGHT // 2 + 15))\n        text(SCREEN, "L 키: 로비로 돌아가기", 22, GOLD, (WIDTH // 2, HEIGHT // 2 + 55))\n        text(SCREEN, "ESC 키: 게임 종료", 18, (220, 210, 201), (WIDTH // 2, HEIGHT // 2 + 95))\n\n    elif game["state"] == "clear":\n        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)\n        overlay.fill((20, 12, 25, 225))\n        SCREEN.blit(overlay, (0, 0))\n\n        pygame.draw.rect(SCREEN, GOLD, (WIDTH // 2 - 350, HEIGHT // 2 - 190, 700, 340), width=4, border_radius=16)\n        \n        text(SCREEN, "★ VICTORY! ★", 72, GOLD, (WIDTH // 2, HEIGHT // 2 - 110), True)\n        text(SCREEN, "국어의 모든 시련과 피날레를 완벽하게 돌파했다!", 23, WHITE, (WIDTH // 2, HEIGHT // 2 - 30), True)\n        text(SCREEN, "당신은 진정한 국어의 마스터입니다!", 21, (255, 230, 150), (WIDTH // 2, HEIGHT // 2 + 12), True)\n        \n        text(SCREEN, "R 키: 다시 플레이", 21, (242, 223, 183), (WIDTH // 2, HEIGHT // 2 + 75))\n        text(SCREEN, "L 키: 로비로 돌아가기", 21, GOLD, (WIDTH // 2, HEIGHT // 2 + 115))\n\n    pygame.display.flip()\n\n\ndef draw_hud(surface):\n    text(surface, "PLAYER HP", 17, INK, (155, 170), True)\n\n    for i in range(MAX_HP):\n        rect = pygame.Rect(105 + i * 38, 188, 29, 18)\n        color = RED if i < game["hp"] else (206, 190, 157)\n        pygame.draw.rect(surface, color, rect, border_radius=4)\n\n    page_str = "FINAL" if game["stage"] == "final_hard_book" else ("PAGE 2" if "page2" in game["stage"] else "PAGE 1")\n    text(surface, f"{page_str}", 18, INK, (1020, 169), True)\n\n    stage_names = {\n        "page1_p1": "1페이지: 가나다라 탄막",\n        "page1_p2": "1페이지: 문장 압박 (6회)",\n        "page1_p3": "1페이지: 세로 책 덮기",\n        "page2_mix": "2페이지: 거대해진 혼합 탄막 (6회)",\n        "page2_grammar": "2페이지: 맞춤법 선택 퀴즈 (4문제)",\n        "final_hard_book": "피날레: 하드 모드 책 덮기 (4연속)"\n    }\n\n    draw_panel = pygame.Rect(405, 157, 390, 33)\n    pygame.draw.rect(surface, (255, 247, 223), draw_panel, border_radius=8)\n    pygame.draw.rect(surface, (205, 176, 127), draw_panel, width=2, border_radius=8)\n    text(surface, stage_names.get(game["stage"], ""), 17, INK, draw_panel.center, True)\n    text(surface, "WASD 이동     SPACE 점프     L 로비로", 16, (112, 81, 53), (WIDTH // 2, 690))\n\n\ndef main():\n    running = True\n    while running:\n        dt = min(CLOCK.tick(FPS) / 1000.0, 0.025)\n\n        for event in pygame.event.get():\n            if event.type == pygame.QUIT:\n                running = False\n            elif event.type == pygame.MOUSEBUTTONDOWN and game["state"] == "lobby":\n                btn_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 10, 320, 65)\n                if btn_rect.collidepoint(event.pos):\n                    game.clear()\n                    game.update(new_game())\n                    game["state"] = "playing"\n            elif event.type == pygame.KEYDOWN:\n                if event.key == pygame.K_ESCAPE:\n                    running = False\n                elif event.key == pygame.K_RETURN:\n                    if game["state"] == "lobby":\n                        game.clear()\n                        game.update(new_game())\n                        game["state"] = "playing"\n                elif event.key == pygame.K_SPACE:\n                    if game["state"] == "playing":\n                        jump_player(game["player"])\n                elif event.key == pygame.K_r:\n                    if game["state"] in ("dead", "clear"):\n                        game.clear()\n                        game.update(new_game())\n                        game["state"] = "playing"\n                elif event.key == pygame.K_l:\n                    if game["state"] in ("playing", "dead", "clear"):\n                        game.clear()\n                        game.update(new_game())\n                        game["state"] = "lobby"\n\n        keys = pygame.key.get_pressed()\n        update_game(dt, keys)\n        render()\n\n    pygame.quit()\n    sys.exit()\n\n\nif __name__ == "__main__":\n    main()'
korean_boss = types.ModuleType("embedded_korean_boss")
exec(compile(_korean_source, "Korean Boss Game (embedded)", "exec"), korean_boss.__dict__)

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
screen_mode = "input"  # input -> tutorial -> playing -> stage1_clear -> stage2_ready -> stage3_ready -> ranking
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
    math_cleared = (300 - b_hp_left) if final_stage == 2 else (300 if final_stage > 2 else 0)
    if status == "Clear" and final_stage >= 2:
        math_cleared = 300
    korean_cleared = 500 if status == "Clear" and final_stage == 3 else 0

    score = english_cleared + math_cleared + korean_cleared
    if status == "Clear":
        detail = f"올클리어 (잔여 HP: {p_hp_left})"
    elif final_stage == 3:
        detail = f"국어 보스 도전 중 패배 (남은 HP: {p_hp_left})"
    elif final_stage == 2:
        detail = f"수학 보스 도전 중 패배 (잡은 체력: {english_cleared + (300 - b_hp_left)})"
    else:
        detail = f"영어 보스 도전 중 패배 (잡은 체력: {english_cleared})"

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

            # 비밀 단축키: Shift+M으로 현재 보스 하나 건너뛰기
            if (event.key == pygame.K_m and event.mod & pygame.KMOD_SHIFT
                    and screen_mode == "playing"):
                if stage == 1:
                    bullets.clear()
                    shots.clear()
                    screen_mode = "stage1_clear"
                elif stage == 2:
                    bullets.clear()
                    shots.clear()
                    factor_bullets.clear()
                    circle_hazards.clear()
                    screen_mode = "stage3_ready"
                    stage = 3
                    korean_boss.game.clear()
                    korean_boss.game.update(korean_boss.new_game())
                elif stage == 3:
                    record_result("Clear", 3, 0, korean_boss.game["hp"])
                    screen_mode = "ranking"
                    pygame.key.start_text_input()
                continue

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
                    if stage == 3:
                        korean_boss.jump_player(korean_boss.game["player"])
                    else:
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

            elif screen_mode == "stage3_ready":
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    korean_boss.game.clear()
                    korean_boss.game.update(korean_boss.new_game())
                    korean_boss.game["state"] = "playing"
                    screen_mode = "playing"
                    stage = 3

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
        if stage != 3:
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
                            # 수학 보스 클리어 후 국어 보스로 진행
                            screen_mode = "stage3_ready"
                            stage = 3
                            korean_boss.game.clear()
                            korean_boss.game.update(korean_boss.new_game())
                            bullets.clear()
                            shots.clear()
                            factor_bullets.clear()
                            circle_hazards.clear()
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

        if stage == 3:
            korean_keys = pygame.key.get_pressed()
            korean_boss.update_game(min(clock.get_time() / 1000.0, 0.025), korean_keys)
            if korean_boss.game["state"] in ("dead", "clear"):
                status = "Clear" if korean_boss.game["state"] == "clear" else "Lose"
                record_result(status, 3, 0, korean_boss.game["hp"])
                screen_mode = "ranking"
                pygame.key.start_text_input()

        if stage != 3:
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
    elif screen_mode == "stage3_ready":
        screen.fill(BLACK)
        draw_background_stars()
        draw_centered_text("STAGE 3: 최종보스- 국어의 왕", pygame.Rect(0, H // 2 - 150, W, 80), RED, BIG)
        draw_centered_text("맞춤법과 문장, 책의 시련을 돌파하고, 점프를 적극 활용해 끝까지 살아남으세요!", pygame.Rect(0, H // 2 - 50, W, 60), WHITE, FONT)
        draw_centered_text("ENTER를 눌러 국어 보스전을 시작하세요!", pygame.Rect(0, H // 2 + 45, W, 60), YELLOW, FONT)
    elif screen_mode == "playing" and stage == 3:
        korean_boss.render()
        screen.blit(pygame.transform.scale(korean_boss.SCREEN, (W, H)), (0, 0))
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
            draw_text("STAGE 2: 수학의 지배자", W // 2 - 230, H // 2 - 100, GREEN, BIG)
            draw_text("명제 퀴즈와 4사분면 최종 시험이 기다립니다.", W // 2 - 270, H // 2 - 20, WHITE, FONT)
            draw_text("ENTER를 눌러 전투를 시작하세요!", W // 2 - 220, H // 2 + 50, YELLOW, FONT)

    pygame.display.flip()

pygame.quit()
