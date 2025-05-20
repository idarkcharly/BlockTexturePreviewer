import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import sin, cos, radians
import json
import sys
import os

# Coordenadas de los vértices del cubo
vertices = (
    (0.5, 0.0, -0.5),
    (0.5, 1.0, -0.5),
    (-0.5, 1.0, -0.5),
    (-0.5, 0.0, -0.5),
    (0.5, 0.0, 0.5),
    (0.5, 1.0, 0.5),
    (-0.5, 0.0, 0.5),
    (-0.5, 1.0, 0.5),
)

# Índices de los vértices que forman cada cara del cubo
faces = (
    (0, 1, 2, 3),  # cara trasera
    (4, 5, 1, 0),  # cara derecha
    (6, 7, 5, 4),  # cara frontal
    (3, 2, 7, 6),  # cara izquierda
    (1, 5, 7, 2),  # cara superior
    (4, 0, 3, 6),  # cara inferior
)

# Coordenadas de textura por vértice
tex_coords = (
    (0, 1),
    (0, 0),
    (1, 0),
    (1, 1),
)


# Carga una textura desde un archivo PNG y la prepara para OpenGL
def load_texture(path):
    if not os.path.isfile(path):
        print(f"Archivo de textura no encontrado: {path}")
        return None

    surface = pygame.image.load(path)
    surface = pygame.transform.flip(surface, False, True)
    data = pygame.image.tostring(surface, "RGBA", True)
    width, height = surface.get_size()

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data
    )
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    return tex_id


# Dibuja un cubo con las texturas aplicadas a cada cara
def draw_cube(face_textures):
    for i, face in enumerate(faces):
        tex_id = face_textures.get(i)
        if tex_id is None:
            continue

        glBindTexture(GL_TEXTURE_2D, tex_id)
        glBegin(GL_QUADS)
        for j in range(4):
            glTexCoord2f(*tex_coords[j])
            glVertex3f(*vertices[face[j]])
        glEnd()


# Dibuja los ejes X (rojo), Y (verde) y Z (azul) para referencia
def draw_axes():
    glDisable(GL_TEXTURE_2D)
    glLineWidth(2)
    glBegin(GL_LINES)
    glColor3f(1.0, 0.0, 0.0)  # Eje X
    glVertex3f(-10, 0, 0)
    glVertex3f(10, 0, 0)
    glColor3f(0.0, 1.0, 0.0)  # Eje Y
    glVertex3f(0, -10, 0)
    glVertex3f(0, 10, 0)
    glColor3f(0.0, 0.5, 1.0)  # Eje Z
    glVertex3f(0, 0, -10)
    glVertex3f(0, 0, 10)
    glEnd()
    glColor3f(1, 1, 1)
    glEnable(GL_TEXTURE_2D)


# Dibuja una cuadrícula sobre el plano XZ para orientación visual
def draw_grid():
    glDisable(GL_TEXTURE_2D)
    glColor3f(0.4, 0.4, 0.4)
    glBegin(GL_LINES)
    for i in range(-10, 11):
        glVertex3f(i, 0, -10)
        glVertex3f(i, 0, 10)
        glVertex3f(-10, 0, i)
        glVertex3f(10, 0, i)
    glEnd()
    glColor3f(1, 1, 1)
    glEnable(GL_TEXTURE_2D)


# Convierte una ruta de textura de Minecraft a una ruta válida de archivo PNG
def parse_texture_path(mc_path, base_folder):
    if mc_path.startswith("minecraft:"):
        mc_path = mc_path[len("minecraft:") :]
    return os.path.join(base_folder, "textures", mc_path + ".png")


# Asigna las texturas cargadas a las caras del cubo según el tipo de modelo
def assign_textures_to_faces(parent, textures):
    parent_lower = parent.lower()

    # Modelos con top, bottom y side
    if (
        ("cube_top_bottom" in parent_lower)
        or ("top_bottom" in parent_lower)
        or ("bottom_top" in parent_lower)
    ):
        top = textures.get("top")
        bottom = textures.get("bottom")
        side = textures.get("side")
        if not (top and bottom and side):
            print(
                "Faltan texturas para modelo con top, bottom y side (top, bottom, side)"
            )
            return None
        return {0: side, 1: side, 2: side, 3: side, 4: top, 5: bottom}

    # Modelos de columna (troncos, madera, etc.)
    elif (
        ("cube_column" in parent_lower)
        or ("log" in parent_lower)
        or ("wood" in parent_lower)
    ):
        end = textures.get("end")
        side = textures.get("side")
        if not (end and side):
            print("Faltan texturas para modelo columna (end, side)")
            return None
        return {0: side, 1: side, 2: side, 3: side, 4: end, 5: end}

    # Modelos completamente cúbicos (una sola textura)
    elif (
        ("cube_all" in parent_lower)
        or ("leaves" in parent_lower)
        or ("cube" in parent_lower)
    ):
        texture = textures.get("all") or list(textures.values())[0]
        return {i: texture for i in range(6)}

    else:
        print(f"Modelo no soportado o muy complejo: {parent}")
        return None


# Función principal del programa
def main():
    pygame.init()
    pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    glViewport(0, 0, 800, 600)
    pygame.display.set_caption("Minecraft Block Texture Previewer")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0.2, 0.2, 0.2, 1.0)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 800 / 600, 0.1, 1000)
    glMatrixMode(GL_MODELVIEW)

    # Obtiene la ruta relativa del archivo, compatible con .py y .exe
    def get_relative_path(filename):
        if getattr(sys, "frozen", False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, filename)

    path_json = get_relative_path("path.json")
    if not os.path.isfile(path_json):
        print("No se encontró el archivo path.json junto al ejecutable.")
        return

    with open(path_json, "r") as f:
        path_data = json.load(f)

    model_path = path_data.get("model_path")
    if not model_path:
        print("No se encontró 'model_path' en path.json")
        return
    if not os.path.isfile(model_path):
        print(f"Archivo modelo no encontrado: {model_path}")
        return

    base_folder = os.path.dirname(model_path)

    # Carga el archivo JSON del modelo
    with open(model_path, "r") as f:
        model_data = json.load(f)

    parent = model_data.get("parent", "")
    textures_raw = model_data.get("textures", {})

    # Carga todas las texturas necesarias
    textures_loaded = {}
    for key, mc_path in textures_raw.items():
        ruta = parse_texture_path(mc_path, base_folder)
        tex_id = load_texture(ruta)
        if tex_id is None:
            print(f"Error cargando textura '{key}' desde: {ruta}")
            return
        textures_loaded[key] = tex_id

    face_textures = assign_textures_to_faces(parent, textures_loaded)
    if face_textures is None:
        print("No se pudo asignar texturas a las caras.")
        return

    distance = 6
    angle_x, angle_y = 25, 30
    mouse_down = False
    last_mouse = (0, 0)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:
                    mouse_down = True
                    last_mouse = pygame.mouse.get_pos()
                elif event.button == 4:
                    distance = max(1, distance - 0.5)
                elif event.button == 5:
                    distance = min(100, distance + 0.5)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    mouse_down = False

            elif event.type == pygame.MOUSEMOTION and mouse_down:
                x, y = pygame.mouse.get_pos()
                dx = x - last_mouse[0]
                dy = y - last_mouse[1]
                last_mouse = (x, y)

                angle_y -= dx * 0.3
                angle_x -= dy * 0.3
                angle_x = max(-89.9, min(89.9, angle_x))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        cam_x = distance * sin(radians(angle_y)) * cos(radians(angle_x))
        cam_y = distance * sin(radians(angle_x))
        cam_z = distance * cos(radians(angle_y)) * cos(radians(angle_x))
        gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 1, 0)

        draw_axes()
        draw_grid()
        draw_cube(face_textures)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
