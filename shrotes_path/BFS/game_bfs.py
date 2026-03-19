import pygame
import sys
from BFS import *

# ===== PARAMETRES =====
CELL_SIZE = 15
ROWS, COLS = 40, 40

WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE + 90

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Éditeur + BFS")

font = pygame.font.SysFont(None, 24)

# ===== ETAT =====
grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]

start = None
goal = None

mode = "edit"  # "edit" ou "run"

brightness = {}
path_cells = set()

# init brightness
def reset_visual():
    brightness.clear()
    path_cells.clear()
    for x in range(ROWS):
        for y in range(COLS):
            brightness[(x,y)] = 0.0

reset_visual()

bfs_gen = None

clock = pygame.time.Clock()

# ===== OUTILS =====
def get_cell_from_mouse(pos):
    x = pos[1] // CELL_SIZE
    y = pos[0] // CELL_SIZE
    return x, y

# ===== LOOP =====
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ===== CLIC SOURIS =====
        if mode == "edit":
            if pygame.mouse.get_pressed()[0]:  # clic gauche
                x, y = get_cell_from_mouse(pygame.mouse.get_pos())
                if 0 <= x < ROWS and 0 <= y < COLS:
                    grid[x][y] = 0  # mur

            if pygame.mouse.get_pressed()[2]:  # clic droit
                x, y = get_cell_from_mouse(pygame.mouse.get_pos())
                if 0 <= x < ROWS and 0 <= y < COLS:
                    grid[x][y] = 1  # enlever mur

        # ===== CLAVIER =====
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                x, y = get_cell_from_mouse(pygame.mouse.get_pos())
                start = (x, y)

            if event.key == pygame.K_g:
                x, y = get_cell_from_mouse(pygame.mouse.get_pos())
                goal = (x, y)

            if event.key == pygame.K_SPACE and start and goal:
                # lancer BFS
                mode = "run"
                reset_visual()
                bfs_gen = bfs(grid, start, goal, ROWS, COLS)

            if event.key == pygame.K_r:
                mode = "edit"
                reset_visual()

    # ===== BFS =====
    if mode == "run" and bfs_gen:
        for _ in range(20):
            try:
                action, node = next(bfs_gen)

                if action == "Exploration":
                    brightness[node] = 0.3

                elif action == "path":
                    path_cells.add(node)

            except StopIteration:
                break

    # ===== DRAW =====
    screen.fill((0,0,0))

    for x in range(ROWS):
        for y in range(COLS):
            rect = pygame.Rect(y*CELL_SIZE, x*CELL_SIZE, CELL_SIZE, CELL_SIZE)

            if grid[x][y] == 0:
                pygame.draw.rect(screen, (0,0,0), rect)
            else:
                b = brightness[(x,y)]
                color = (
                    int(20 + (120-20)*b),
                    int(20 + (180-20)*b),
                    int(60 + (255-60)*b),
                )
                pygame.draw.rect(screen, color, rect)

            if (x,y) in path_cells:
                pygame.draw.rect(screen, (255,255,0), rect)

    # start / goal
    if start:
        pygame.draw.rect(screen, (0,255,0),
            (start[1]*CELL_SIZE, start[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    if goal:
        pygame.draw.rect(screen, (255,0,0),
            (goal[1]*CELL_SIZE, goal[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # ===== TEXTE =====
    legend = [
        "Clic gauche = mur",
        "Clic droit = effacer",
        "S = départ | G = objectif",
        "SPACE = lancer BFS",
        "R = reset"
    ]

    for i, text in enumerate(legend):
        img = font.render(text, True, (255,255,255))
        screen.blit(img, (10, ROWS*CELL_SIZE + 5 + i*15))

    pygame.display.flip()

pygame.quit()
sys.exit()