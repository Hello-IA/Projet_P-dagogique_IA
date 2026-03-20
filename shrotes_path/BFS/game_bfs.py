import pygame
import sys
from BFS import *
from Dijkstra import * 
from A_star import *
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

# ===== TERRAINS =====
terrains = [
    {"name":"Facile", "cost":1, "color":(20,120,255)},   # bleu
    {"name":"Moyen",  "cost":3, "color":(180,140,50)},   # brun
    {"name":"Difficile","cost":5,"color":(120,30,30)},   # rouge
]
terrain_actif = terrains[0]

def check_click_terrain(pos):
    for i, t in enumerate(terrains):
        rect = pygame.Rect(10 + i*60, 10, 50, 30)
        if rect.collidepoint(pos):
            return t
    return None

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
                selection = check_click_terrain(event.pos)
                if selection:
                    terrain_actif = selection
                elif 0 <= x < ROWS and 0 <= y < COLS:
                    grid[x][y] = 0  # mur

            if pygame.mouse.get_pressed()[2]:  # clic droit
                x, y = get_cell_from_mouse(pygame.mouse.get_pos())
                if 0 <= x < ROWS and 0 <= y < COLS:
                    grid[x][y] = terrain_actif["cost"]  # enlever mur
                    

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
                bfs_gen = A_star(grid, start, goal, ROWS, COLS)

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
            val = grid[x][y]
            if grid[x][y] == 0:
                pygame.draw.rect(screen, (0,0,0), rect)
            else:
                base_color = next(t["color"] for t in terrains if t["cost"]==val)
                b = brightness[(x,y)]
                
                color = (
                    int(base_color[0]*b + (base_color[0]//2)*(1-b)),
                    int(base_color[1]*b + (base_color[1]//2)*(1-b)),
                    int(base_color[2]*b + (base_color[2]//2)*(1-b)),
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


    # ===== Panneau terrain =====
    for i, t in enumerate(terrains):
        rect = pygame.Rect(10 + i*60, 10, 50, 30)
        pygame.draw.rect(screen, t["color"], rect)
        if t == terrain_actif:
            pygame.draw.rect(screen, (255,255,255), rect, 3)  # bordure blanche si actif
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