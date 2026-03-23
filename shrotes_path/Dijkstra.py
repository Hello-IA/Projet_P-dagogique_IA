import math
def Dijkstra(grid, start, goal, ROWS, COLS):
    distence = [[math.inf for _ in range(COLS)] for _ in range(ROWS)]
    sx, sy = start
    distence[sx][sy] = 0
    parent = {}
    non_visite = set((x, y) for x in range(ROWS) for y in range(COLS))
    enter = True
    
    while enter and non_visite != set():
        
        current = sorted(list(non_visite))[0]
        for nv in non_visite:
            
            if distence[nv[0]][nv[1]] == math.inf:
                continue
            
            if distence[current[0]][current[1]] >= distence[nv[0]][nv[1]]:
                current = nv
                
        non_visite.remove(current)
        
        if current == goal:
            enter = False
            
        
        x, y = current
        neighbors = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
            
        for nx, ny in neighbors:
            
            if 0 <= nx < ROWS and 0 <= ny < COLS:
                alt = distence[x][y] + grid[nx][ny]
                
                if grid[nx][ny] != 0 and alt < distence[nx][ny]:
                    distence[nx][ny] = alt
                    parent[(nx, ny)] = current
                    
        yield ("Exploration", current) # permet animation frame par frame
        

    node = goal
    while node in parent:
        node = parent[node]
        yield ("path", node)
    