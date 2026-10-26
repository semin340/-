import json
from pathlib import Path
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
SMALL_FONT = pygame.font.SysFont("malgungothic", 15)
RULE_FONT = pygame.font.SysFont("malgungothic", 17)

BLACK = (10, 8, 20)
WHITE = (245, 245, 255)
RED = (255, 65, 95)
CYAN = (80, 230, 255)
PURPLE = (175, 90, 255)
YELLOW = (255, 220, 80)
GREEN = (100, 255, 150)

LEADERBOARD_FILE = Path(__file__).with_name("soul_jump_ranking.json")
try:
    loaded = json.loads(LEADERBOARD_FILE.read_text(encoding="utf-8"))
    leaderboard = loaded if isinstance(loaded, list) else []
except (FileNotFoundError, json.JSONDecodeError, OSError):
    leaderboard = []

leaderboard = [row for row in leaderboard if isinstance(row, dict)]

screen_mode = "rules"
input_mode = False
active_input = "name"
player_name = ""
student_id = ""

input_box_width = 360
input_box_height = 48
name_box_rect = pygame.Rect((W - input_box_width) // 2, 225, input_box_width, input_box_height)
id_box_rect = pygame.Rect((W - input_box_width) // 2, 315, input_box_width, input_box_height)

# 처음부터 시작 버튼 영역
restart_button = pygame.Rect(190, 510, 420, 55)


def draw_text(text, x, y, color=WHITE, font=FONT):
    image = font.render(str(text), True, color)
    screen.blit(image, (x, y))


def draw_centered_text(text, rect, color=WHITE, font=FONT):
    image = font.render(str(text), True, color)
    screen.blit(image, image.get_rect(center=rect.center))


def draw_background_stars():
    for i in range(35):
        x = (i * 127 + 23) % W
        y = (i * 83 + 17) % H
        pygame.draw.circle(screen, (45, 40, 70), (x, y), 1)


def draw_rules_screen():
    screen.fill(BLACK)
    draw_background_stars()

    title = BIG.render("SOUL JUMP - 게임 규칙", True, CYAN)
    screen.blit(title, title.get_rect(center=(W // 2, 48)))

    rules = [
        ("[ 게임 목표 ]", YELLOW),
        ("수학 보스의 HP를 0으로 만들거나 공격을 피하며 생존하세요.", WHITE),
        ("게임 종료 후 점수, 생존시간, 참가자 랭킹을 확인할 수 있습니다.", WHITE),
        ("[ 조작 방법 ]", YELLOW),
        ("이동: 방향키 또는 W / A / S / D", WHITE),
        ("점프: SPACE  |  공격: Z", WHITE),
        ("점프 중에는 지상 탄환을 피할 수 있습니다.", WHITE),
        ("[ 명제 퀴즈 ]", YELLOW),
        ("화면의 명제를 읽고 판단하세요.", WHITE),
        ("공격해야 하면 제한 시간 안에 Z를 누르세요.", WHITE),
        ("공격하면 안 되면 Z를 누르지 말고 기다리세요.", WHITE),
        ("정답을 맞히면 보스에게 추가 피해를 줍니다.", WHITE),
        ("오답을 선택하면 플레이어 HP가 감소할 수 있습니다.", WHITE),
        ("[ 점수 및 랭킹 ]", YELLOW),
        ("왼쪽에는 점수와 생존시간, 오른쪽에는 상위 10명이 표시됩니다.", WHITE),
        ("같은 이름과 학번은 더 오래 생존했을 때 기록이 갱신됩니다.", WHITE),
    ]

    y = 92
    for text, color in rules:
        draw_text(text, 58, y, color, RULE_FONT)
        y += 24

    button = pygame.Rect(190, 505, 420, 55)
    pygame.draw.rect(screen, (35, 30, 65), button, border_radius=12)
    pygame.draw.rect(screen, CYAN, button, 2, border_radius=12)
    draw_centered_text("ENTER: 참가자 정보 입력", button, YELLOW)

    draw_centered_text(
        "ESC: 종료", pygame.Rect(0, 566, W, 25),
        (165, 165, 190), SMALL_FONT
    )


def draw_input_screen():
    screen.fill(BLACK)
    draw_background_stars()

    title_image = BIG.render("SOUL JUMP", True, WHITE)
    screen.blit(
        title_image,
        title_image.get_rect(center=(W // 2, 125))
    )

    draw_text(
        "이름", name_box_rect.x - 75, name_box_rect.y + 10,
        YELLOW if active_input == "name" else WHITE
    )
    pygame.draw.rect(
        screen,
        YELLOW if active_input == "name" else (100, 100, 120),
        name_box_rect, 2
    )

    name_display = player_name if player_name else "이름을 입력하세요..."
    draw_text(
        name_display, name_box_rect.x + 12, name_box_rect.y + 12,
        WHITE if player_name else (130, 130, 145)
    )

    draw_text(
        "학번", id_box_rect.x - 75, id_box_rect.y + 10,
        YELLOW if active_input == "student_id" else WHITE
    )
    pygame.draw.rect(
        screen,
        YELLOW if active_input == "student_id" else (100, 100, 120),
        id_box_rect, 2
    )

    id_display = student_id if student_id else "학번을 입력하세요..."
    draw_text(
        id_display, id_box_rect.x + 12, id_box_rect.y + 12,
        WHITE if student_id else (130, 130, 145)
    )

    if player_name.strip() and student_id.strip():
        draw_centered_text(
            "ENTER: 랭킹 확인",
            pygame.Rect(200, 395, 400, 40), YELLOW, FONT
        )
    else:
        draw_centered_text(
            "이름과 학번을 모두 입력하세요",
            pygame.Rect(200, 395, 400, 40), RED, FONT
        )

    draw_centered_text(
        "TAB / 방향키로 입력칸 이동",
        pygame.Rect(200, 435, 400, 30), CYAN, SMALL_FONT
    )
    draw_centered_text(
        "ESC: 종료",
        pygame.Rect(200, 470, 400, 30),
        (165, 165, 190), SMALL_FONT
    )


def draw_ranking_screen():
    screen.fill(BLACK)
    draw_background_stars()

    title = BIG.render("SOUL JUMP - 점수 랭킹", True, CYAN)
    screen.blit(title, title.get_rect(center=(W // 2, 48)))
    draw_centered_text(
        f"참가자: {player_name}  |  학번: {student_id}",
        pygame.Rect(80, 82, 640, 30), YELLOW, SMALL_FONT
    )

    panel = pygame.Rect(65, 125, 670, 355)
    pygame.draw.rect(screen, (25, 22, 42), panel, border_radius=12)
    pygame.draw.rect(screen, PURPLE, panel, 2, border_radius=12)

    draw_text("순위", 105, 145, CYAN, FONT)
    draw_text("학번", 205, 145, CYAN, FONT)
    draw_text("이름", 390, 145, CYAN, FONT)
    draw_text("점수", 550, 145, CYAN, FONT)
    pygame.draw.line(screen, (90, 85, 125), (90, 178), (710, 178), 1)

    ranked = sorted(
        leaderboard,
        key=lambda row: int(row.get("score", 0) or 0),
        reverse=True,
    )
    if not ranked:
        draw_centered_text("아직 저장된 점수 기록이 없습니다.",
                            pygame.Rect(100, 215, 600, 40), WHITE, FONT)
    else:
        for rank, row in enumerate(ranked[:10], start=1):
            y = 190 + (rank - 1) * 27
            name = str(row.get("name", "알 수 없음"))[:10]
            sid = str(row.get("student_id", "-"))[:14]
            score = int(row.get("score", 0) or 0)
            highlight = sid == student_id and name == player_name
            color = YELLOW if highlight else WHITE
            draw_text(f"{rank:>2}.", 105, y, color, SMALL_FONT)
            draw_text(sid, 205, y, color, SMALL_FONT)
            draw_text(name, 390, y, color, SMALL_FONT)
            draw_text(f"{score:,}점", 550, y, color, SMALL_FONT)

    pygame.draw.rect(screen, (35, 30, 65), restart_button, border_radius=12)
    pygame.draw.rect(screen, CYAN, restart_button, 2, border_radius=12)
    draw_centered_text("처음부터 시작", restart_button, YELLOW, FONT)
    draw_centered_text("ENTER: 처음부터 시작   |   ESC: 종료",
                       pygame.Rect(0, 570, W, 22), (165, 165, 190), SMALL_FONT)


running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                break

            if screen_mode == "rules":
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    player_name = ""
                    student_id = ""
                    active_input = "name"
                    screen_mode = "input"
                    input_mode = True
                    pygame.key.start_text_input()

            elif screen_mode == "input":
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if player_name.strip() and student_id.strip():
                        input_mode = False
                        pygame.key.stop_text_input()
                        screen_mode = "ranking"
                elif event.key == pygame.K_BACKSPACE:
                    if active_input == "name":
                        player_name = player_name[:-1]
                    else:
                        student_id = student_id[:-1]
                elif event.key in (pygame.K_TAB, pygame.K_UP, pygame.K_DOWN):
                    active_input = "student_id" if active_input == "name" else "name"

            elif screen_mode == "ranking":
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    screen_mode = "rules"
                    input_mode = False

        if screen_mode == "input" and event.type == pygame.TEXTINPUT:
            if active_input == "name" and len(player_name) < 10:
                player_name += event.text
            elif active_input == "student_id" and len(student_id) < 15 and event.text.isdigit():
                student_id += event.text

        if screen_mode == "input" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if name_box_rect.collidepoint(event.pos):
                active_input = "name"
            elif id_box_rect.collidepoint(event.pos):
                active_input = "student_id"

        if screen_mode == "ranking" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if restart_button.collidepoint(event.pos):
                screen_mode = "rules"
                input_mode = False

    if not running:
        break

    if screen_mode == "rules":
        draw_rules_screen()
    elif screen_mode == "input":
        draw_input_screen()
    else:
        draw_ranking_screen()

    pygame.display.flip()

pygame.quit()
