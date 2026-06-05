import pygame
import sys
import random
import math

pygame.init()

ANCHO, ALTO = 700, 800
FPS = 60
NIVELES_MAX = 10
TAM_PIXEL = 3

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 85)
ROJO_OSCURO = (150, 0, 50)
CYAN = (0, 255, 255)
CYAN_OSCURO = (0, 150, 150)
MAGENTA = (255, 0, 255)
AMARILLO = (255, 230, 0)
VERDE = (0, 255, 100)
NARANJA = (255, 140, 0)
PURPURA = (180, 0, 255)
AZUL = (0, 100, 255)
ROSA = (255, 105, 180)
DORADO = (255, 215, 0)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("GALAGA NEON - 10 BOSSES CHALLENGE")
reloj = pygame.time.Clock()

SPRITE_JUGADOR = [
    [0,0,0,0,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,1,1,1,1,0,0,0,0,0],
    [0,0,0,1,1,2,2,1,1,0,0,0,0],
    [0,0,1,1,2,2,2,2,1,1,0,0,0],
    [0,1,1,2,2,1,1,2,2,1,1,0,0],
    [1,1,2,2,1,1,1,1,2,2,1,1,0],
    [1,2,2,1,1,1,1,1,1,2,2,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,1,1,1,1,1,1,1,1,1,1,1,0],
    [0,0,1,1,0,0,0,0,0,1,1,0,0],
]

SPRITE_ENEMIGO1 = [
    [0,0,0,1,1,1,1,1,1,0,0,0],
    [0,0,1,1,2,2,2,2,1,1,0,0],
    [0,1,1,2,2,1,1,2,2,1,1,0],
    [1,1,2,2,1,1,1,1,2,2,1,1],
    [1,2,2,1,1,1,1,1,1,2,2,1],
    [1,1,1,1,2,2,2,2,1,1,1,1],
    [0,1,1,2,1,1,1,1,2,1,1,0],
    [0,0,1,1,0,0,0,0,1,1,0,0],
    [0,1,1,0,0,0,0,0,0,1,1,0],
    [1,1,0,0,0,0,0,0,0,0,1,1],
]

SPRITE_ENEMIGO2 = [
    [0,0,1,0,0,0,0,0,0,1,0,0],
    [0,1,1,1,0,0,0,0,1,1,1,0],
    [1,1,2,1,1,1,1,1,1,2,1,1],
    [1,2,2,1,1,2,2,1,1,2,2,1],
    [1,1,2,1,1,1,1,1,1,2,1,1],
    [0,1,1,1,2,2,2,2,1,1,1,0],
    [0,0,1,1,1,1,1,1,1,1,0,0],
    [0,0,0,1,0,0,0,0,1,0,0,0],
    [0,0,1,0,0,0,0,0,0,1,0,0],
    [0,1,0,0,0,0,0,0,0,0,1,0],
]

SPRITE_ENEMIGO3 = [
    [0,0,0,1,1,1,1,1,1,0,0,0],
    [0,0,1,1,2,2,2,2,1,1,0,0],
    [0,1,1,2,1,1,1,1,2,1,1,0],
    [1,1,2,1,1,2,2,1,1,2,1,1],
    [1,2,2,1,1,1,1,1,1,2,2,1],
    [1,1,2,1,2,2,2,2,1,2,1,1],
    [0,1,1,1,1,1,1,1,1,1,1,0],
    [0,0,1,1,0,0,0,0,1,1,0,0],
    [0,1,1,0,0,0,0,0,0,1,1,0],
    [1,1,0,0,0,0,0,0,0,0,1,1],
]

SPRITES_JEFES = [
    [[0,0,0,0,0,0,1,1,0,0,0,0,0,0],
     [0,0,0,0,0,1,1,1,1,0,0,0,0,0],
     [0,0,0,0,1,1,2,2,1,1,0,0,0,0],
     [0,0,0,1,1,2,2,2,2,1,1,0,0,0],
     [0,0,1,1,2,2,1,1,2,2,1,1,0,0],
     [0,1,1,2,2,1,1,1,1,2,2,1,1,0],
     [1,1,2,2,1,1,1,1,1,1,2,2,1,1],
     [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
     [0,1,1,1,1,1,1,1,1,1,1,1,1,0],
     [0,0,1,1,0,0,0,0,0,0,1,1,0,0]],
    [[1,0,0,0,0,0,0,0,0,0,0,0,0,1],
     [1,1,0,0,0,0,0,0,0,0,0,0,1,1],
     [1,1,1,0,0,0,0,0,0,0,0,1,1,1],
     [1,1,1,1,0,0,0,0,0,0,1,1,1,1],
     [0,1,1,1,1,2,2,2,2,1,1,1,1,0],
     [0,0,1,1,1,1,1,1,1,1,1,1,0,0],
     [0,0,0,1,1,1,1,1,1,1,1,0,0,0],
     [0,0,0,0,1,1,1,1,1,1,0,0,0,0],
     [0,0,0,0,0,1,1,1,1,0,0,0,0,0],
     [0,0,0,0,0,0,1,1,0,0,0,0,0,0]],
    [[0,0,0,1,1,1,1,1,1,1,1,0,0,0],
     [0,0,1,1,2,2,2,2,2,2,1,1,0,0],
     [0,1,1,2,2,1,1,1,1,2,2,1,1,0],
     [1,1,2,2,1,1,2,2,1,1,2,2,1,1],
     [1,2,2,1,1,2,2,2,2,1,1,2,2,1],
     [1,2,2,1,1,2,2,2,2,1,1,2,2,1],
     [1,1,2,2,1,1,2,2,1,1,2,2,1,1],
     [0,1,1,2,2,1,1,1,1,2,2,1,1,0],
     [0,0,1,1,2,2,2,2,2,2,1,1,0,0],
     [0,0,0,1,1,1,1,1,1,1,1,0,0,0]],
    [[0,0,0,0,0,0,1,1,0,0,0,0,0,0],
     [0,0,0,0,0,1,1,1,1,0,0,0,0,0],
     [0,0,0,0,1,1,2,2,1,1,0,0,0,0],
     [0,0,0,1,1,2,2,2,2,1,1,0,0,0],
     [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
     [0,1,1,1,1,1,1,1,1,1,1,1,1,0],
     [0,0,1,1,1,1,1,1,1,1,1,1,0,0],
     [0,0,0,1,1,1,1,1,1,1,1,0,0,0],
     [0,0,0,0,1,1,0,0,1,1,0,0,0,0],
     [0,0,0,0,1,1,0,0,1,1,0,0,0,0]],
    [[0,0,0,0,0,1,1,1,1,0,0,0,0,0],
     [0,0,0,0,1,1,2,2,1,1,0,0,0,0],
     [0,0,0,1,1,2,2,2,2,1,1,0,0,0],
     [0,0,1,1,2,2,1,1,2,2,1,1,0,0],
     [0,1,1,2,2,1,1,1,1,2,2,1,1,0],
     [1,1,2,2,1,1,1,1,1,1,2,2,1,1],
     [0,1,1,2,2,1,1,1,1,2,2,1,1,0],
     [0,0,1,1,2,2,1,1,2,2,1,1,0,0],
     [0,0,0,1,1,2,2,2,2,1,1,0,0,0],
     [0,0,0,0,1,1,2,2,1,1,0,0,0,0]],
    [[0,0,1,1,1,1,1,1,1,1,1,1,0,0],
     [0,1,1,2,2,2,2,2,2,2,2,1,1,0],
     [1,1,2,2,1,1,1,1,1,1,2,2,1,1],
     [1,2,2,1,1,1,1,1,1,1,1,2,2,1],
     [1,2,2,1,1,1,1,1,1,1,1,2,2,1],
     [1,2,2,1,1,1,1,1,1,1,1,2,2,1],
     [1,1,2,2,1,1,1,1,1,1,2,2,1,1],
     [0,1,1,2,2,2,2,2,2,2,2,1,1,0],
     [0,0,1,1,1,1,1,1,1,1,1,1,0,0],
     [0,0,0,1,1,0,0,0,0,1,1,0,0,0]],
    [[0,0,0,0,1,1,0,0,1,1,0,0,0,0],
     [0,0,0,1,1,1,1,1,1,1,1,0,0,0],
     [0,0,1,1,2,2,1,1,2,2,1,1,0,0],
     [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
     [1,1,2,1,1,1,1,1,1,1,1,2,1,1],
     [1,1,2,1,1,1,1,1,1,1,1,2,1,1],
     [0,1,1,1,1,1,1,1,1,1,1,1,1,0],
     [0,0,1,1,1,1,1,1,1,1,1,1,0,0],
     [0,0,0,1,1,0,0,0,0,1,1,0,0,0],
     [0,0,0,0,1,0,0,0,0,1,0,0,0,0]],
    [[0,0,0,0,1,1,1,1,1,1,0,0,0,0],
     [0,0,0,0,1,1,1,1,1,1,0,0,0,0],
     [0,0,0,0,1,1,2,2,1,1,0,0,0,0],
     [1,1,1,1,1,1,2,2,1,1,1,1,1,1],
     [1,1,1,1,2,2,1,1,2,2,1,1,1,1],
     [1,1,1,1,2,2,1,1,2,2,1,1,1,1],
     [0,0,0,0,1,1,2,2,1,1,0,0,0,0],
     [0,0,0,0,1,1,1,1,1,1,0,0,0,0],
     [0,0,0,0,1,1,1,1,1,1,0,0,0,0],
     [0,0,0,0,0,1,1,1,1,0,0,0,0,0]],
    [[0,0,0,1,1,1,1,1,1,1,1,0,0,0],
     [0,0,1,1,2,2,2,2,2,2,1,1,0,0],
     [0,1,1,2,2,1,1,1,1,2,2,1,1,0],
     [1,1,2,2,1,1,2,2,1,1,2,2,1,1],
     [1,2,2,1,1,2,2,2,2,1,1,2,2,1],
     [1,2,2,1,1,2,2,2,2,1,1,2,2,1],
     [1,1,2,2,1,1,2,2,1,1,2,2,1,1],
     [0,1,1,2,2,1,1,1,1,2,2,1,1,0],
     [0,0,1,1,2,2,2,2,2,2,1,1,0,0],
     [0,0,0,1,1,1,1,1,1,1,1,0,0,0]],
    [[0,0,0,0,1,1,1,1,1,1,0,0,0,0],
     [0,0,0,1,1,2,2,2,2,1,1,0,0,0],
     [0,0,1,1,2,3,3,3,3,2,1,1,0,0],
     [0,1,1,2,3,1,1,1,1,3,2,1,1,0],
     [1,1,2,3,1,1,2,2,1,1,3,2,1,1],
     [1,2,3,1,1,2,2,2,2,1,1,3,2,1],
     [1,2,3,1,1,2,2,2,2,1,1,3,2,1],
     [1,1,2,3,1,1,2,2,1,1,3,2,1,1],
     [0,1,1,2,3,1,1,1,1,3,2,1,1,0],
     [0,0,1,1,2,3,3,3,3,2,1,1,0,0]],
]

COLORES_JEFES = [
    {1: VERDE, 2: BLANCO},
    {1: NARANJA, 2: BLANCO},
    {1: AZUL, 2: BLANCO},
    {1: PURPURA, 2: BLANCO},
    {1: ROSA, 2: BLANCO},
    {1: AMARILLO, 2: BLANCO},
    {1: CYAN, 2: BLANCO},
    {1: ROJO, 2: BLANCO},
    {1: MAGENTA, 2: BLANCO},
    {1: DORADO, 2: BLANCO, 3: ROJO},
]

NOMBRES_JEFES = [
    "GREEN STRIKER", "ORANGE VIPER", "BLUE ORBITER", "PURPLE ARROW",
    "PINK DIAMOND", "YELLOW SHIELD", "CYAN STAR", "RED CRUSHER",
    "MAGENTA HEX", "GOLDEN FINAL BOSS"
]

SPRITE_BALA = [[0,1,0],[1,1,1],[1,1,1],[0,1,0]]

try:
    f_titulo = pygame.font.SysFont('consolas', 48, bold=True)
    f_texto = pygame.font.SysFont('consolas', 24, bold=True)
    f_pequena = pygame.font.SysFont('consolas', 18, bold=True)
except:
    f_titulo = pygame.font.Font(None, 48)
    f_texto = pygame.font.Font(None, 24)
    f_pequena = pygame.font.Font(None, 18)

def dibujar_sprite(sprite, x, y, colores, tam_pixel=TAM_PIXEL):
    for fila_idx, fila in enumerate(sprite):
        for col_idx, pixel in enumerate(fila):
            if pixel != 0:
                color = colores.get(pixel, BLANCO)
                rect = pygame.Rect(int(x) + col_idx * tam_pixel, int(y) + fila_idx * tam_pixel, tam_pixel, tam_pixel)
                if rect.right > 0 and rect.left < ANCHO and rect.bottom > 0 and rect.top < ALTO:
                    pygame.draw.rect(pantalla, color, rect)

def dibujar_sprite_con_alas(sprite, x, y, colores, tam_pixel=TAM_PIXEL, frame=0):
    for fila_idx, fila in enumerate(sprite):
        for col_idx, pixel in enumerate(fila):
            if pixel != 0:
                color = colores.get(pixel, BLANCO)
                offset = 0
                if frame == 1 and (col_idx < 2 or col_idx > len(fila) - 3):
                    offset = 1
                rect = pygame.Rect(int(x) + col_idx * tam_pixel + offset, int(y) + fila_idx * tam_pixel, tam_pixel, tam_pixel)
                if rect.right > 0 and rect.left < ANCHO and rect.bottom > 0 and rect.top < ALTO:
                    pygame.draw.rect(pantalla, color, rect)

def dibujar_texto_neon(texto, fuente, color, x, y, centro=True):
    t = fuente.render(texto, True, color)
    r = t.get_rect()
    if centro: r.center = (x, y)
    else: r.topleft = (x, y)
    for i in range(3, 0, -1):
        g = pygame.transform.scale(t, (t.get_width()+i*4, t.get_height()+i*4))
        gr = g.get_rect(center=r.center)
        gs = pygame.Surface(g.get_size(), pygame.SRCALPHA)
        gs.fill((*color, 50))
        pantalla.blit(gs, gr.topleft)
    pantalla.blit(t, r.topleft)

class Estrella:
    def __init__(self):
        self.reset()
        self.y = random.randint(0, ALTO)
    def reset(self):
        self.x = random.randint(0, ANCHO)
        self.y = -5
        self.size = random.choice([1, 2])
        self.speed = random.uniform(0.3, 1.5)
        self.color = random.choice([BLANCO, CYAN, ROJO, AMARILLO, MAGENTA, VERDE])
    def actualizar(self):
        self.y += self.speed
        if self.y > ALTO: self.reset()
    def dibujar(self):
        pygame.draw.rect(pantalla, self.color, (int(self.x), int(self.y), self.size, self.size))

class Particula:
    def __init__(self, x, y, color, size=None):
        self.x, self.y = float(x), float(y)
        self.color = color
        angulo = random.uniform(0, math.pi*2)
        velocidad = random.uniform(1, 6)
        self.vx = math.cos(angulo) * velocidad
        self.vy = math.sin(angulo) * velocidad
        self.life = random.randint(20, 40)
        self.max_life = self.life
        self.size = size if size else random.randint(2, 5)
    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1
    def dibujar(self):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            surf = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            pantalla.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

class FlashScreen:
    def __init__(self):
        self.alpha = 0
        self.color = BLANCO
    def activar(self, color=BLANCO, intensidad=100):
        self.alpha = intensidad
        self.color = color
    def actualizar(self):
        if self.alpha > 0:
            self.alpha -= 5
            if self.alpha < 0: self.alpha = 0
    def dibujar(self):
        if self.alpha > 0:
            s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            s.fill((*self.color, self.alpha))
            pantalla.blit(s, (0, 0))

class ScreenShake:
    def __init__(self):
        self.intensidad = 0
        self.duracion = 0
        self.offset_x = 0
        self.offset_y = 0
    def activar(self, intensidad=5, duracion=10):
        self.intensidad = intensidad
        self.duracion = duracion
    def actualizar(self):
        if self.duracion > 0:
            self.duracion -= 1
            self.offset_x = random.randint(-self.intensidad, self.intensidad)
            self.offset_y = random.randint(-self.intensidad, self.intensidad)
        else:
            self.offset_x = 0
            self.offset_y = 0
    def aplicar(self):
        return (self.offset_x, self.offset_y)

class Jugador:
    def __init__(self):
        self.w = 13 * TAM_PIXEL
        self.h = 10 * TAM_PIXEL
        self.x = ANCHO//2 - self.w//2
        self.y = ALTO - 120
        self.speed = 5
        self.vidas = 3
        self.cooldown = 0
        self.invulnerable = 0
        self.colores = {1: CYAN, 2: BLANCO}
        self.frame = 0
        self.frame_timer = 0

    def mover(self, teclas):
        if teclas[pygame.K_LEFT] and self.x > 0: self.x -= self.speed
        if teclas[pygame.K_RIGHT] and self.x < ANCHO - self.w: self.x += self.speed

    def disparar(self, balas):
        if self.cooldown <= 0:
            balas.append(Bala(self.x + self.w//2 - 2, self.y, -9, True))
            self.cooldown = 12

    def actualizar(self):
        if self.cooldown > 0: self.cooldown -= 1
        if self.invulnerable > 0: self.invulnerable -= 1
        self.frame_timer += 1
        if self.frame_timer > 10:
            self.frame = 1 - self.frame
            self.frame_timer = 0

    def dibujar(self):
        if self.invulnerable > 0 and (self.invulnerable // 4) % 2 == 0: return
        dibujar_sprite_con_alas(SPRITE_JUGADOR, self.x, self.y, self.colores, TAM_PIXEL, self.frame)

class Enemigo:
    def __init__(self, x, y, tipo, nivel):
        self.x = float(x)
        self.y = float(y)
        self.tipo = tipo
        self.w = 12 * TAM_PIXEL
        self.h = 10 * TAM_PIXEL
        self.estado = 'formacion'
        self.angulo_bajada = 0
        self.direccion = 1
        self.objetivo_y = float(y)
        self.frame = 0
        self.frame_timer = 0
        self.timer_disparo = random.randint(200, 400)

        if nivel <= 3:
            self.velocidad_base = 0.5
        elif nivel <= 7:
            self.velocidad_base = 0.9
        else:
            self.velocidad_base = 1.3
        self.velocidad_base += nivel * 0.08

        sprites = [SPRITE_ENEMIGO1, SPRITE_ENEMIGO2, SPRITE_ENEMIGO3]
        colores_list = [{1: CYAN, 2: BLANCO}, {1: MAGENTA, 2: BLANCO}, {1: ROJO, 2: AMARILLO}]
        self.sprite = sprites[tipo-1]
        self.colores = colores_list[tipo-1]
        self.puntos = tipo * 100

    def actualizar(self, formacion_offset_x):
        self.frame_timer += 1
        if self.frame_timer > 20:
            self.frame = 1 - self.frame
            self.frame_timer = 0

        if self.estado == 'formacion':
            self.x += self.velocidad_base * self.direccion
            if self.x < 10: self.x = 10
            if self.x > ANCHO - self.w - 10: self.x = ANCHO - self.w - 10
        elif self.estado == 'bajando':
            self.angulo_bajada += 0.05
            self.x += math.sin(self.angulo_bajada) * 2
            self.y += 2.5
            if self.y > ALTO - 150: self.estado = 'subiendo'
        elif self.estado == 'subiendo':
            self.y -= 2
            if self.y <= self.objetivo_y:
                self.estado = 'formacion'
                self.y = self.objetivo_y

    def dibujar(self):
        dibujar_sprite_con_alas(self.sprite, int(self.x), int(self.y), self.colores, TAM_PIXEL, self.frame)

    def disparar(self, balas, nivel):
        self.timer_disparo -= 1
        if self.timer_disparo <= 0 and self.estado == 'formacion':
            balas.append(Bala(self.x + self.w//2, self.y + self.h, 4 + nivel*0.2, False))
            if nivel <= 3:
                self.timer_disparo = random.randint(300, 500)
            elif nivel <= 7:
                self.timer_disparo = random.randint(150, 250)
            else:
                self.timer_disparo = random.randint(60, 120)

class Jefe:
    def __init__(self, nivel):
        self.nivel = nivel
        sprite = SPRITES_JEFES[nivel-1]
        self.w = len(sprite[0]) * TAM_PIXEL
        self.h = len(sprite) * TAM_PIXEL
        self.x = float(ANCHO//2 - self.w//2)
        self.y = -float(self.h)
        self.objetivo_y = 80.0
        self.estado = 'entrando'
        self.frame = 0
        self.frame_timer = 0
        self.puntos = 1000 + (nivel * 500)

        self.vida_max = 15 + (nivel * 8)
        self.vida = self.vida_max

        self.timer_patron = 0
        self.duracion_patron = 200
        self.angulo_circular = 0
        self.centro_x = float(ANCHO//2)
        self.centro_y = 150.0
        self.radio_circular = 120.0
        self.direccion_x = 1.0
        self.direccion_y = 1.0
        self.velocidad = 1.2 + (nivel * 0.3)

        self.timer_disparo = 60

        self.sprite = sprite
        self.colores = COLORES_JEFES[nivel-1]
        self.nombre = NOMBRES_JEFES[nivel-1]
        self.nombre_patron = ['simple', 'abanico', 'circular', 'laser', 'espiral',
                              'dirigido', 'doble_lateral', 'cruz', 'rafaga', 'caotico'][nivel-1]

    def actualizar(self, balas_enemigo, jugador_x, jugador_y):
        self.frame_timer += 1
        if self.frame_timer > 15:
            self.frame = 1 - self.frame
            self.frame_timer = 0

        if self.estado == 'entrando':
            self.y += 2
            if self.y >= self.objetivo_y:
                self.estado = 'peleando'
        elif self.estado == 'peleando':
            self.timer_patron += 1
            if self.timer_patron >= self.duracion_patron:
                self.timer_patron = 0

            if self.nivel <= 3:
                self.x += self.velocidad * self.direccion_x
                if self.x <= 30:
                    self.x = 30
                    self.direccion_x *= -1
                elif self.x >= ANCHO - self.w - 30:
                    self.x = ANCHO - self.w - 30
                    self.direccion_x *= -1
            elif self.nivel <= 7:
                self.x += self.velocidad * self.direccion_x
                self.y = self.objetivo_y + math.sin(self.timer_patron * 0.03) * 40
                if self.x <= 30:
                    self.x = 30
                    self.direccion_x *= -1
                elif self.x >= ANCHO - self.w - 30:
                    self.x = ANCHO - self.w - 30
                    self.direccion_x *= -1
            else:
                self.angulo_circular += 0.02 + (self.nivel * 0.003)
                nueva_x = self.centro_x + math.cos(self.angulo_circular) * self.radio_circular - self.w//2
                nueva_y = self.objetivo_y + math.sin(self.angulo_circular * 1.5) * 60
                self.x = max(30, min(ANCHO - self.w - 30, nueva_x))
                self.y = max(60, min(300, nueva_y))

            self.timer_disparo -= 1
            if self.timer_disparo <= 0:
                self.ejecutar_patron_disparo(balas_enemigo, jugador_x, jugador_y)
                self.resetear_timer_disparo()

    def ejecutar_patron_disparo(self, balas, jugador_x, jugador_y):
        cx = self.x + self.w//2
        cy = self.y + self.h

        if self.nombre_patron == 'simple':
            balas.append(Bala(cx, cy, 5, False))
        elif self.nombre_patron == 'abanico':
            for dx in [-12, 0, 12]:
                balas.append(Bala(cx + dx, cy, 5, False))
        elif self.nombre_patron == 'circular':
            for i in range(8):
                angulo = (math.pi * 2 / 8) * i
                balas.append(BalaDirigida(cx, cy, math.cos(angulo) * 3.5, math.sin(angulo) * 3.5, False))
        elif self.nombre_patron == 'laser':
            for i in range(5):
                balas.append(Bala(cx, cy + i*4, 7, False))
        elif self.nombre_patron == 'espiral':
            angulo = self.timer_patron * 0.2
            balas.append(BalaDirigida(cx, cy, math.cos(angulo) * 4, math.sin(angulo) * 4, False))
            balas.append(BalaDirigida(cx, cy, math.cos(angulo + math.pi) * 4, math.sin(angulo + math.pi) * 4, False))
        elif self.nombre_patron == 'dirigido':
            dx = jugador_x - cx
            dy = jugador_y - cy
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                balas.append(BalaDirigida(cx, cy, (dx/dist) * 4.5, (dy/dist) * 4.5, False))
        elif self.nombre_patron == 'doble_lateral':
            balas.append(Bala(self.x, cy, 5, False))
            balas.append(Bala(self.x + self.w, cy, 5, False))
        elif self.nombre_patron == 'cruz':
            balas.append(Bala(cx, cy, 6, False))
            balas.append(Bala(cx - 15, cy, 5, False))
            balas.append(Bala(cx + 15, cy, 5, False))
        elif self.nombre_patron == 'rafaga':
            for i in range(8):
                angulo = random.uniform(0.2, math.pi - 0.2)
                balas.append(BalaDirigida(cx, cy, math.cos(angulo) * 4, math.sin(angulo) * 4, False))
        elif self.nombre_patron == 'caotico':
            for i in range(10):
                angulo = random.uniform(0, math.pi * 2)
                velocidad = random.uniform(3, 6)
                balas.append(BalaDirigida(cx, cy, math.cos(angulo) * velocidad, math.sin(angulo) * velocidad, False))

    def resetear_timer_disparo(self):
        if self.nivel <= 3:
            self.timer_disparo = random.randint(90, 130)
        elif self.nivel <= 7:
            self.timer_disparo = random.randint(50, 80)
        else:
            self.timer_disparo = random.randint(25, 50)

    def recibir_danio(self):
        self.vida -= 1
        return self.vida <= 0

    def dibujar(self):
        if self.estado == 'entrando' or self.estado == 'peleando':
            dibujar_sprite_con_alas(self.sprite, int(self.x), int(self.y), self.colores, TAM_PIXEL, self.frame)

            bar_width = self.w
            bar_height = 8
            bar_x = int(self.x)
            bar_y = int(self.y) - 20
            vida_ratio = max(0, self.vida / self.vida_max)

            pygame.draw.rect(pantalla, ROJO_OSCURO, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(pantalla, VERDE, (bar_x, bar_y, int(bar_width * vida_ratio), bar_height))
            pygame.draw.rect(pantalla, BLANCO, (bar_x, bar_y, bar_width, bar_height), 2)

            fuente = pygame.font.SysFont('consolas', 14, bold=True)
            texto = fuente.render(self.nombre, True, AMARILLO)
            pantalla.blit(texto, (bar_x + (bar_width - texto.get_width())//2, bar_y - 18))

class Bala:
    def __init__(self, x, y, vy, es_jugador):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = float(vy)
        self.es_jugador = es_jugador
        self.w = 3 * TAM_PIXEL
        self.h = 4 * TAM_PIXEL
        self.activo = True
        self.colores = {1: BLANCO} if es_jugador else {1: AMARILLO}

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        if self.y < -20 or self.y > ALTO + 20 or self.x < -20 or self.x > ANCHO + 20:
            self.activo = False

    def dibujar(self):
        dibujar_sprite(SPRITE_BALA, int(self.x), int(self.y), self.colores, TAM_PIXEL)

class BalaDirigida(Bala):
    def __init__(self, x, y, vx, vy, es_jugador):
        super().__init__(x, y, vy, es_jugador)
        self.vx = float(vx)
        self.vy = float(vy)

class Juego:
    def __init__(self):
        self.estado = 'menu'
        self.nivel = 1
        self.puntaje = 0
        self.high_score = 0
        try:
            with open('highscore_galaga.txt', 'r') as f: self.high_score = int(f.read())
        except: pass

        self.jugador = Jugador()
        self.enemigos = []
        self.jefe = None
        self.balas_jugador = []
        self.balas_enemigo = []
        self.particulas = []
        self.estrellas = [Estrella() for _ in range(150)]

        self.formacion_offset_x = 0
        self.formacion_direccion = 1
        self.fase_jefe = False

        self.flash = FlashScreen()
        self.shake = ScreenShake()

        self.crear_nivel()

    def crear_nivel(self):
        self.enemigos = []
        self.jefe = None
        self.fase_jefe = False

        if self.nivel <= 3:
            filas = 3
            cols = 6 + self.nivel
        elif self.nivel <= 7:
            filas = 4
            cols = 7 + self.nivel
        else:
            filas = 5
            cols = 8 + self.nivel

        cols = min(cols, 10)

        for r in range(filas):
            for c in range(cols):
                tipo = 3 if r == 0 else (2 if r == 1 else 1)
                x = 130 + c * 42
                y = 130 + r * 42
                e = Enemigo(x, y, tipo, self.nivel)
                e.objetivo_y = float(y)
                self.enemigos.append(e)

    def iniciar_fase_jefe(self):
        self.fase_jefe = True
        self.jefe = Jefe(self.nivel)
        self.balas_enemigo.clear()
        self.flash.activar(AMARILLO, 80)
        self.shake.activar(8, 15)

    def crear_explosion(self, x, y, color, cantidad=20):
        for _ in range(cantidad):
            self.particulas.append(Particula(x, y, color))

    def actualizar(self):
        for e in self.estrellas: e.actualizar()
        for p in self.particulas[:]:
            p.actualizar()
            if p.life <= 0: self.particulas.remove(p)

        self.flash.actualizar()
        self.shake.actualizar()

        if self.estado != 'jugando': return

        teclas = pygame.key.get_pressed()
        self.jugador.mover(teclas)
        self.jugador.actualizar()
        if teclas[pygame.K_SPACE]: self.jugador.disparar(self.balas_jugador)

        if not self.fase_jefe:
            self.formacion_offset_x += 0.7 * self.formacion_direccion
            if self.formacion_offset_x > 40 or self.formacion_offset_x < -40:
                self.formacion_direccion *= -1
                for e in self.enemigos:
                    e.direccion = self.formacion_direccion

            for e in self.enemigos:
                e.actualizar(self.formacion_offset_x)
                if random.random() < 0.0015 * self.nivel and e.estado == 'formacion':
                    e.estado = 'bajando'
                e.disparar(self.balas_enemigo, self.nivel)

            if len(self.enemigos) == 0:
                self.iniciar_fase_jefe()
        else:
            if self.jefe:
                self.jefe.actualizar(self.balas_enemigo, self.jugador.x + self.jugador.w//2, self.jugador.y)

        for b in self.balas_jugador[:]:
            b.actualizar()
            if not b.activo: self.balas_jugador.remove(b)
        for b in self.balas_enemigo[:]:
            b.actualizar()
            if not b.activo: self.balas_enemigo.remove(b)

        for b in self.balas_jugador:
            if not b.activo: continue
            for e in self.enemigos[:]:
                if b.activo and self.colision_rect(b.x, b.y, b.w, b.h, e.x, e.y, e.w, e.h):
                    b.activo = False
                    self.crear_explosion(e.x + e.w//2, e.y + e.h//2, e.colores[1], 15)
                    self.puntaje += e.puntos
                    self.enemigos.remove(e)
                    break

        if self.fase_jefe and self.jefe and self.jefe.estado == 'peleando':
            for b in self.balas_jugador:
                if b.activo and self.colision_rect(b.x, b.y, b.w, b.h, self.jefe.x, self.jefe.y, self.jefe.w, self.jefe.h):
                    b.activo = False
                    self.crear_explosion(b.x, b.y, AMARILLO, 8)
                    if self.jefe.recibir_danio():
                        self.crear_explosion(self.jefe.x + self.jefe.w//2, self.jefe.y + self.jefe.h//2,
                                           self.jefe.colores[1], 40)
                        self.puntaje += self.jefe.puntos
                        self.flash.activar(BLANCO, 150)
                        self.shake.activar(12, 20)
                        self.jefe = None

                        if self.nivel < NIVELES_MAX:
                            self.nivel += 1
                            self.crear_nivel()
                            self.balas_jugador.clear()
                            self.balas_enemigo.clear()
                        else:
                            self.estado = 'victoria'
                    break

        if self.jugador.invulnerable <= 0:
            for b in self.balas_enemigo:
                if b.activo and self.colision_rect(b.x, b.y, b.w, b.h, self.jugador.x, self.jugador.y, self.jugador.w, self.jugador.h):
                    self.jugador.vidas -= 1
                    self.jugador.invulnerable = 120
                    self.crear_explosion(self.jugador.x + self.jugador.w//2, self.jugador.y + self.jugador.h//2, CYAN, 25)
                    self.shake.activar(8, 15)
                    self.flash.activar(ROJO, 100)
                    if self.jugador.vidas <= 0:
                        self.estado = 'gameover'
                        if self.puntaje > self.high_score:
                            self.high_score = self.puntaje
                            with open('highscore_galaga.txt', 'w') as f: f.write(str(self.high_score))
                    b.activo = False
                    break

    def colision_rect(self, x1, y1, w1, h1, x2, y2, w2, h2):
        return (x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2)

    def dibujar(self):
        pantalla.fill(NEGRO)

        for e in self.estrellas: e.dibujar()

        if self.estado == 'menu':
            pygame.draw.rect(pantalla, ROJO, (20, 20, ANCHO-40, ALTO-40), 3)
            dibujar_texto_neon("GALAGA", f_titulo, ROJO, ANCHO//2, 150)
            dibujar_texto_neon("10 BOSSES CHALLENGE", f_texto, AMARILLO, ANCHO//2, 220)
            dibujar_texto_neon("HIGH SCORE", f_pequena, ROJO, ANCHO//2, 280)
            dibujar_texto_neon(str(self.high_score), f_texto, BLANCO, ANCHO//2, 320)
            dibujar_texto_neon("PRESS ENTER TO START", f_pequena, CYAN, ANCHO//2, 450)
            dibujar_texto_neon("← → MOVE | SPACE SHOOT", f_pequena, VERDE, ANCHO//2, 490)

        elif self.estado == 'jugando':
            self.jugador.dibujar()
            for e in self.enemigos: e.dibujar()
            if self.jefe: self.jefe.dibujar()
            for b in self.balas_jugador + self.balas_enemigo: b.dibujar()
            for p in self.particulas: p.dibujar()

            pygame.draw.rect(pantalla, ROJO, (0, 0, ANCHO, 3), 2)
            dibujar_texto_neon("HIGH SCORE", f_pequena, ROJO, ANCHO//2, 15)
            dibujar_texto_neon(str(self.high_score), f_pequena, BLANCO, ANCHO//2, 40)
            dibujar_texto_neon(str(self.puntaje), f_pequena, BLANCO, 30, 40, False)
            dibujar_texto_neon(f"LV {self.nivel}", f_pequena, AMARILLO, ANCHO - 80, 40, False)

            if self.fase_jefe and self.jefe:
                dibujar_texto_neon(f"BOSS: {self.jefe.nombre}", f_pequena, ROJO, ANCHO//2, 70)

            for i in range(self.jugador.vidas):
                dibujar_sprite(SPRITE_JUGADOR, 30 + i*40, ALTO - 40, {1: CYAN, 2: BLANCO}, 2)

        elif self.estado == 'gameover':
            self.jugador.dibujar()
            for e in self.enemigos: e.dibujar()
            if self.jefe: self.jefe.dibujar()
            for b in self.balas_jugador + self.balas_enemigo: b.dibujar()
            for p in self.particulas: p.dibujar()

            s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            pantalla.blit(s, (0, 0))

            dibujar_texto_neon("GAME OVER", f_titulo, ROJO, ANCHO//2, ALTO//2 - 50)
            dibujar_texto_neon(f"SCORE: {self.puntaje}", f_texto, BLANCO, ANCHO//2, ALTO//2 + 20)
            dibujar_texto_neon("PRESS ENTER", f_pequena, CYAN, ANCHO//2, ALTO//2 + 80)

        elif self.estado == 'victoria':
            s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            pantalla.blit(s, (0, 0))

            dibujar_texto_neon("VICTORY!", f_titulo, DORADO, ANCHO//2, ALTO//2 - 50)
            dibujar_texto_neon(f"FINAL SCORE: {self.puntaje}", f_texto, BLANCO, ANCHO//2, ALTO//2 + 20)
            dibujar_texto_neon("PRESS ENTER", f_pequena, CYAN, ANCHO//2, ALTO//2 + 80)

        self.flash.dibujar()

        for y in range(0, ALTO, 3):
            pygame.draw.line(pantalla, (0, 0, 0, 30), (0, y), (ANCHO, y))

        pygame.display.flip()

def main():
    juego = Juego()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    if juego.estado == 'menu':
                        juego.estado = 'jugando'
                        juego.nivel = 1; juego.puntaje = 0
                        juego.jugador = Jugador(); juego.crear_nivel()
                    elif juego.estado == 'gameover':
                        juego.estado = 'jugando'
                        juego.nivel = 1; juego.puntaje = 0
                        juego.jugador = Jugador(); juego.crear_nivel()
                    elif juego.estado == 'victoria':
                        juego.estado = 'menu'
        juego.actualizar()
        juego.dibujar()
        reloj.tick(FPS)

if __name__ == "__main__":
    main()
