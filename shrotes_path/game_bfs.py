import pygame
import sys
from BFS import *
from Dijkstra import * 
from A_star import *
import math
# ===== PARAMETRES =====
CELL_SIZE = 16
ROWS, COLS = 40, 40

WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE + 100
algo_actif = "BFS"

score = 0
pygame.init()

# chargement du sprite pour les murs


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Éditeur BFS/Dijkstra/A*")

font = pygame.font.SysFont(None, 24)

TILE_SIZE = 16

sprite_maptiles = pygame.image.load("Tiles\\maptiles.png").convert_alpha()

# Dimensions de l'image
width, height = sprite_maptiles.get_size()

tiles = []

for y in range(0, height, TILE_SIZE):
    row = []
    for x in range(0, width, TILE_SIZE):
        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        tile = sprite_maptiles.subsurface(rect)
        row.append(tile)
    tiles.append(row)
    
rect = pygame.Rect(64, 80, 48, 48)
grass = sprite_maptiles.subsurface(rect) 

rect = pygame.Rect(64, 144, 48, 48)
montaine = sprite_maptiles.subsurface(rect) 

rect = pygame.Rect(128, 0, 48, 48)
snow = sprite_maptiles.subsurface(rect)    

TILE_SIZE_UNIT = 32

sprite_units = pygame.image.load("Tiles\\units.png").convert_alpha()

# Dimensions de l'image
width, height = sprite_units.get_size()

units = []

for y in range(0, height, TILE_SIZE_UNIT):
    row = []
    for x in range(0, width, TILE_SIZE_UNIT):
        rect = pygame.Rect(x, y, TILE_SIZE_UNIT, TILE_SIZE_UNIT)
        unit = sprite_units.subsurface(rect)
        row.append(unit)
    units.append(row)

player_BFS = units[0][3]
player_BFS = pygame.transform.scale(player_BFS, (CELL_SIZE, CELL_SIZE))

sprite_castle = pygame.image.load("Tiles\\lilcastle.png").convert_alpha()

rect = pygame.Rect(0, 0, 32, 32)
castle = sprite_castle.subsurface(rect)
castle = pygame.transform.scale(castle, (CELL_SIZE, CELL_SIZE))

sprite_way = pygame.image.load("Tiles\\way.png").convert_alpha()
way = pygame.transform.scale(sprite_way, (CELL_SIZE, CELL_SIZE))



# ===== ETAT =====
grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]

start = None
goal = None

mode = "edit"  # "edit" ou "run"

brightness = {}
path_cells = set()
path_parent = {}
parent = None
# init brightness
def reset_visual():
    brightness.clear()
    path_cells.clear()
    path_parent.clear()
    parent = None
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
    {"name":"Grass", "cost":1, "sprite":grass},   # bleu
    {"name":"Montaine",  "cost":3, "sprite":montaine},   # brun
    {"name":"snow","cost":5,"sprite":snow},   # rouge
]
terrain_actif = terrains[0]

def check_click_terrain(pos):
    for i, t in enumerate(terrains):
        rect = pygame.Rect(10 + i*60, 10, 48, 48)
        if rect.collidepoint(pos):
            return t
    return None

def generate_tiles(x, y, center, tl, bl, tr, br):
    voisin_8 = []
    for i in range(-1, 2):
        voisin = []
        for j in range(-1, 2):
            if 0 <= x+i < ROWS and 0 <= y+j < COLS:
                val_voisin = grid[x+i][y+j]
            else:
                val_voisin = math.inf
            voisin.append(val_voisin)
        voisin_8.append(voisin)
    tile = pygame.Surface((16, 16), pygame.SRCALPHA)
    
    tl_small, tr_small, bl_small, br_small = None, None, None, None
    val = grid[x][y]
    size = 8
    tl_small = pygame.transform.scale(tiles[center[0]][center[1]], (size, size))
    tr_small = pygame.transform.scale(tiles[center[0]][center[1]], (size, size))
    bl_small = pygame.transform.scale(tiles[center[0]][center[1]], (size, size))
    br_small = pygame.transform.scale(tiles[center[0]][center[1]], (size, size))
    #le coint en au a gauche
    if voisin_8[1][0] != val and voisin_8[0][1] != val:
        tl_small = pygame.transform.scale(tiles[tl[0][0]][tl[0][1]], (size, size))
    elif voisin_8[1][0] == val and voisin_8[0][1] == val and voisin_8[0][0] != val:
        tl_small = pygame.transform.scale(tiles[tl[1][0]][tl[1][1]], (size, size))
    elif voisin_8[1][0] != val and voisin_8[0][1] == val:
        tl_small = pygame.transform.scale(tiles[tl[2][0]][tl[2][1]], (size, size))
    elif voisin_8[1][0] == val and voisin_8[0][1] != val:
        tl_small = pygame.transform.scale(tiles[tl[3][0]][tl[3][1]], (size, size))
        
    #le coins en bas a gauche
    if voisin_8[1][0] != val and voisin_8[2][1] != val:
        bl_small = pygame.transform.scale(tiles[bl[0][0]][bl[0][1]], (size, size))
    elif voisin_8[1][0] == val and voisin_8[2][1] == val and voisin_8[2][0] != val:
        bl_small = pygame.transform.scale(tiles[bl[1][0]][bl[1][1]], (size, size))
    elif voisin_8[1][0] != val and voisin_8[2][1] == val:
        bl_small = pygame.transform.scale(tiles[bl[2][0]][bl[2][1]], (size, size))
    elif voisin_8[1][0] == val and voisin_8[2][1] != val:
        bl_small = pygame.transform.scale(tiles[bl[3][0]][bl[3][1]], (size, size))
        
    #le coint en hau a droite
    if voisin_8[1][2] != val and voisin_8[0][1] != val:
        tr_small = pygame.transform.scale(tiles[tr[0][0]][tr[0][1]], (size, size))
    elif voisin_8[1][2] == val and voisin_8[0][1] == val and voisin_8[0][2] != val:
        tr_small = pygame.transform.scale(tiles[tr[1][0]][tr[1][1]], (size, size))
    elif voisin_8[1][2] != val and voisin_8[0][1] == val:
        tr_small = pygame.transform.scale(tiles[tr[2][0]][tr[2][1]], (size, size))
    elif voisin_8[1][2] == val and voisin_8[0][1] != val:
        tr_small = pygame.transform.scale(tiles[tr[3][0]][tr[3][1]], (size, size))
    
    #le coint en bas a droite
    if voisin_8[1][2] != val and voisin_8[2][1] != val:
        br_small = pygame.transform.scale(tiles[br[0][0]][br[0][1]], (size, size))
    elif voisin_8[1][2] == val and voisin_8[2][1] == val and voisin_8[2][2] != val:
        br_small = pygame.transform.scale(tiles[br[1][0]][br[1][1]], (size, size))
    elif voisin_8[1][2] != val and voisin_8[2][1] == val:
        br_small = pygame.transform.scale(tiles[br[2][0]][br[2][1]], (size, size))
    elif voisin_8[1][2] == val and voisin_8[2][1] != val:
        br_small = pygame.transform.scale(tiles[br[3][0]][br[3][1]], (size, size))
        
    tile.blit(tl_small, (0, 0))
    tile.blit(tr_small, (8, 0))
    tile.blit(bl_small, (0, 8))
    tile.blit(br_small, (8, 8))
    return tile

def check_click_algo(pos):
    buttons = ["BFS", "DIJKSTRA", "ASTAR"]
    for i, name in enumerate(buttons):
        rect = pygame.Rect(250 + i*110, 10, 100, 30)
        if rect.collidepoint(pos):
            return name
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
                selection_algo = check_click_algo(event.pos)
                if selection_algo:
                    algo_actif = selection_algo
                elif selection:
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
                score = 0
                if algo_actif == "DIJKSTRA":
                    bfs_gen = Dijkstra(grid, start, goal, ROWS, COLS)
                elif algo_actif == "ASTAR":
                    bfs_gen = A_star(grid, start, goal, ROWS, COLS)
                else:
                    bfs_gen = bfs(grid, start, goal, ROWS, COLS)
                    
                    
                    

            if event.key == pygame.K_r:
                mode = "edit"
                reset_visual()
    
    # ===== BFS =====
    if mode == "run" and bfs_gen:
        for _ in range(20):
            try:
                action, node,  = next(bfs_gen)

                if action == "Exploration":
                    brightness[node] = 1

                elif action == "path":
                    path_cells.add(node)
                    path_parent[node] = parent
                    parent = node
                    score += grid[node[0]][node[1]]

            except StopIteration:
                break

    # ===== DRAW =====
    screen.fill((0,0,0))

    for x in range(ROWS):
        for y in range(COLS):
            rect = pygame.Rect(y*CELL_SIZE, x*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            if grid[x][y] == 0:
                #pygame.draw.rect(screen, (0,0,0), rect)
                # affiche le sprite à la place du mur
                tl = ((1, 12), (0, 14), (2, 12), (1, 13))
                bl = ((3, 12), (1, 11), (2, 12), (3, 13))
                tr = ((1, 14), (0, 13), (2, 14), (1, 13))
                br = ((3, 14), (2, 11), (2, 14), (3, 13))
                tile = generate_tiles(x, y, (2, 13), tl, bl, tr, br)

            else:
                val = grid[x][y]
                terrain = next(t for t in terrains if t["cost"]==val)
                b = brightness[(x,y)]
                
                
                
                if val == 1:
                    tl = ((5, 4), (4, 7), (6, 4), (5, 5))
                    bl = ((7, 4), (5, 7), (6, 4), (7, 5))
                    tr = ((5, 6), (3, 7), (6, 6), (5, 5))
                    br = ((7, 6), (2, 7), (6, 6), (7, 5))
                    tile = generate_tiles(x, y, (6, 5), tl, bl, tr, br)
  
                    
                elif val == 3:
                    tl = ((9, 4), (8, 5), (10, 4), (9, 5))
                    bl = ((11, 4), (9, 7), (10, 4), (11, 5))
                    tr = ((9, 6), (8, 6), (10, 6), (9, 5))
                    br = ((11, 6), (8, 7), (10, 6), (11, 5))
                    tile = generate_tiles(x, y, (10, 5), tl, bl, tr, br)

                    
                elif val == 5:
                    tl = ((0, 8), (4, 9), (1, 8), (0, 9))
                    bl = ((2, 8), (3, 9), (1, 8), (2, 9))
                    tr = ((0, 10), (4, 9), (1, 10), (0, 9))
                    br = ((2, 10), (3, 8), (1, 10), (2, 9))
                    tile = generate_tiles(x, y, (1, 9), tl, bl, tr, br)

                    
            screen.blit(tile, rect)


            if brightness[(x,y)] > 0:
                overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 50))  # léger éclaircissement
                screen.blit(overlay, rect)

            if (x,y) in path_cells and (x, y) != start:
                sprite_path = pygame.transform.rotate(way, 0)
                if path_parent[(x, y)] == (x, y-1) :
                    sprite_path = pygame.transform.rotate(way, 90)
                elif path_parent[(x, y)] == (x-1, y) :
                    sprite_path = pygame.transform.rotate(way, 0)
                elif path_parent[(x, y)] == (x+1, y) :
                    sprite_path = pygame.transform.rotate(way, 180)
                elif path_parent[(x, y)] == (x, y+1) :
                    sprite_path = pygame.transform.rotate(way, -90)
                screen.blit(sprite_path, (rect.x, rect.y))

    # start / goal
    if start:
        screen.blit(player_BFS,
            (start[1]*CELL_SIZE, start[0]*CELL_SIZE))

    if goal:
        screen.blit(castle,
            (goal[1]*CELL_SIZE, goal[0]*CELL_SIZE))

    
    # ===== Panneau terrain =====
    for i, t in enumerate(terrains):
        rect = pygame.Rect(10 + i*60, 10, 48, 48)
        sprite_redim = pygame.transform.scale(t["sprite"], (48, 48))
        screen.blit(sprite_redim, rect)

        
        if t == terrain_actif:
            # overlay blanc transparent
            overlay = pygame.Surface((48, 48), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 80))  # alpha = transparence
            screen.blit(overlay, (rect.x, rect.y))
    

           
        

            
    buttons = ["BFS", "DIJKSTRA", "ASTAR"]

    for i, name in enumerate(buttons):
        rect = pygame.Rect(250 + i*110, 10, 100, 30)

        # couleur différente si actif
        if name == algo_actif:
            pygame.draw.rect(screen, (255,255,255), rect)
            text_color = (0,0,0)
        else:
            pygame.draw.rect(screen, (80,80,80), rect)
            text_color = (255,255,255)

        text = font.render(name, True, text_color)
        screen.blit(text, (rect.x + 10, rect.y + 5))
        
        
    # ===== TEXTE =====
    legend = [
        "Clic gauche = mur",
        "Clic droit = effacer",
        "S = départ | G = objectif",
        "SPACE = lancer BFS",
        "R = reset",
        f"Score : {score}"
    ]

    for i, text in enumerate(legend):
        img = font.render(text, True, (255,255,255))
        screen.blit(img, (10, ROWS*CELL_SIZE + 5 + i*15))

    pygame.display.flip()

pygame.quit()
sys.exit()