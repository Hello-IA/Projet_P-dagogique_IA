from collections import deque


def bfs(grid, start, goal, ROWS, COLS):
    queue = deque([start])
    visited = set([start])
    parent = {}

    while queue:
        current = queue.popleft()

        if current == goal:
            break

        x, y = current
        neighbors = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]

        for nx, ny in neighbors:
            if 0 <= nx < ROWS and 0 <= ny < COLS:
                if grid[nx][ny] == 1 and (nx, ny) not in visited:
                    queue.append((nx, ny))
                    visited.add((nx, ny))
                    parent[(nx, ny)] = current

        yield ("Exploration", current) # permet animation frame par frame

    # reconstruction chemin
    node = goal
    while node in parent:
        node = parent[node]
        yield ("path", node)
