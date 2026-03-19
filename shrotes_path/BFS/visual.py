from ursina import *
import time
from BFS import *


def create_tree(position):
    # tronc
    trunk = Entity(
        model='cube',
        color=color.brown,
        scale=(0.2, 1, 0.2),
        position=(position[0], 0.5, position[1])
    )

    # feuillage
    leaves = Entity(
        model='sphere',
        color=color.green,
        scale=0.8,
        position=(position[0], 1.3, position[1])
    )

# Création de la grille 3D
for x in range(ROWS):
    for y in range(COLS):
        if grid[x][y] == 1:
            create_tree((x, y))
        else:
            cube = Entity(
                model='cube',
                color=color.brown,
                scale=(0.9, 0.1, 0.9),
                position=(x, 0, y)
            )
            cube.color = rgb(0.24, 0.124, 0.124)
            cubes[(x, y)] = cube

# caméra


# activer la caméra libre

class SmoothFreeCamera:
    def __init__(self, speed=10, sensitivity=100):
        self.speed = speed
        self.sensitivity = sensitivity
        mouse.locked = True
        self.yaw = 0
        self.pitch = 0
        taskMgr.add(self.update, "camera_update")

    def update(self, task):
        dt = time.dt

        # déplacement clavier
        forward = Vec3(camera.forward.x, 0, camera.forward.z).normalized()
        right = Vec3(camera.right.x, 0, camera.right.z).normalized()

        move = Vec3(0,0,0)
        if held_keys['w'] or held_keys['z']:
            move += forward
        if held_keys['s']:
            move -= forward
        if held_keys['d']:
            move += right
        if held_keys['q']:
            move -= right

        camera.position += move * self.speed * dt

        # rotation souris (fluide avec dt)
        dx = mouse.velocity[0] * self.sensitivity * dt
        dy = mouse.velocity[1] * self.sensitivity * dt

        self.yaw += dx
        self.pitch -= dy
        self.pitch = clamp(self.pitch, -90, 90)

        camera.rotation_x = self.pitch
        camera.rotation_y = self.yaw

        return task.cont



Sky(color=color.azure)

app = Ursina()

camera.position = (ROWS/2, 20, -75)
camera.rotation_x = 10
SmoothFreeCamera(speed=10, sensitivity=10)
def visual(actions, position):
    if actions == "Exploration":
        # visualisation exploration
        if position != start:
            cubes[position].color = rgb(0.1, 0.6, 0.1)
            cubes[position].scale = 1.2
            invoke(setattr, cubes[position], 'scale', 0.9, delay=0.1)
    if actions == "path" and position != None:
        cubes[position].color = color.blue
    
bfs_gen = bfs()

def update():
    for _ in range(100):  # ← augmente ce nombre
        try:
            actions, position =next(bfs_gen)
            visual(actions, position)
        except StopIteration:
            break

app.run()