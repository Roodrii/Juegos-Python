import pygame
import sys
import random
import math

pygame.init()
pygame.mixer.init()

ANCHO, ALTO = 800, 750
TAM_CELDA = 20
FPS = 60
FPS_JUEGO_INICIAL = 12

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("🐍 NEON SNAKE // ULTRA GAMER EDITION")
reloj = pygame.time.Clock()

NEON_VERDE = (0, 255, 65)
NEON_ROJO = (255, 0, 85)
NEON_CYAN = (0, 255, 255)
NEON_PURPURA = (180, 0, 255)
NEON_AMARILLO = (255, 230, 0)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

try:
    fuente_titulo = pygame.font.SysFont('consolas', 60, bold=True)
    fuente_texto = pygame.font.SysFont('consolas', 28, bold=True)
    fuente_pequena = pygame.font.SysFont('consolas', 20, bold=True)
except:
    fuente_titulo = pygame.font.Font(None, 60)
    fuente_texto = pygame.font.Font(None, 28)
    fuente_pequena = pygame.font.Font(None, 20)

def cargar_sonido(nombre_archivo):
    try:
        return pygame.mixer.Sound(nombre_archivo)
    except:
        return None

sonido_comer = cargar_sonido("comer.wav")
sonido_morir = cargar_sonido("morir.wav")
sonido_power = cargar_sonido("power.wav")

class Particula:
    def __init__(self, x, y, color, vx, vy, size, life):
        self.x, self.y = x, y
        self.color = color
        self.vx, self.vy = vx, vy
        self.size = size
        self.life = life
        self.max_life = life

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 1
        self.size *= 0.95

    def dibujar(self, superficie):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            superficie.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class Estela:
    def __init__(self, x, y, color, size):
        self.x, self.y = x, y
        self.color = color
        self.size = size
        self.life = 25
        self.max_life = 25

    def actualizar(self):
        self.life -= 1
        self.size *= 0.93

    def dibujar(self, superficie):
        if self.life > 0:
            alpha = int(180 * (self.life / self.max_life))
            rect = pygame.Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
            s = pygame.Surface((int(self.size), int(self.size)), pygame.SRCALPHA)
            pygame.draw.rect(s, (*self.color, alpha), s.get_rect(), border_radius=6)
            superficie.blit(s, rect.topleft)

class TextoFlotante:
    def __init__(self, texto, x, y, color, size=24):
        self.texto = texto
        self.x, self.y = x, y
        self.color = color
        self.life = 60
        self.max_life = 60
        self.size = size
        self.vy = -2

    def actualizar(self):
        self.life -= 1
        self.y += self.vy
        self.vy *= 0.95

    def dibujar(self, superficie):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            fuente = pygame.font.SysFont('impact', self.size, bold=True)
            texto_surf = fuente.render(self.texto, True, self.color)
            s = pygame.Surface(texto_surf.get_size(), pygame.SRCALPHA)
            s.blit(texto_surf, (0, 0))
            for i in range(3, 0, -1):
                glow = pygame.transform.scale(texto_surf,
                    (texto_surf.get_width() + i*4, texto_surf.get_height() + i*4))
                glow_rect = glow.get_rect(center=(s.get_width()//2, s.get_height()//2))
                gs = pygame.Surface(glow.get_size(), pygame.SRCALPHA)
                gs.fill((*self.color, alpha // 3))
                s.blit(gs, glow_rect.topleft)
            s.blit(texto_surf, (s.get_width()//2 - texto_surf.get_width()//2,
                               s.get_height()//2 - texto_surf.get_height()//2))
            superficie.blit(s, (int(self.x - s.get_width()//2), int(self.y - s.get_height()//2)))

class ScreenShake:
    def __init__(self):
        self.intensidad = 0
        self.duracion = 0

    def activar(self, intensidad=5, duracion=10):
        self.intensidad = intensidad
        self.duracion = duracion

    def actualizar(self):
        if self.duracion > 0:
            self.duracion -= 1
            return (random.randint(-self.intensidad, self.intensidad),
                    random.randint(-self.intensidad, self.intensidad))
        return (0, 0)

class ParticulaOrbital:
    def __init__(self, centro_x, centro_y, radio, velocidad, color, size=3):
        self.centro_x = centro_x
        self.centro_y = centro_y
        self.radio = radio
        self.angulo = random.uniform(0, math.pi * 2)
        self.velocidad = velocidad
        self.color = color
        self.size = size
        self.life = 60

    def actualizar(self):
        self.angulo += self.velocidad
        self.life -= 1

    def dibujar(self, superficie):
        if self.life > 0:
            x = self.centro_x + math.cos(self.angulo) * self.radio
            y = self.centro_y + math.sin(self.angulo) * self.radio
            alpha = int(255 * (self.life / 60))
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
            superficie.blit(s, (int(x - self.size), int(y - self.size)))

class PowerUp:
    def __init__(self, x, y, tipo):
        self.x, self.y = x, y
        self.tipo = tipo
        self.life = 300
        self.anim_time = 0
        self.particulas_orbitales = []

        if tipo == 'escudo':
            self.color = NEON_CYAN
            self.icono = 'S'
        elif tipo == 'velocidad':
            self.color = NEON_AMARILLO
            self.icono = 'V'
        elif tipo == 'puntos_dobles':
            self.color = NEON_PURPURA
            self.icono = '2X'

    def actualizar(self):
        self.life -= 1
        self.anim_time += 1

        if self.anim_time % 5 == 0:
            self.particulas_orbitales.append(
                ParticulaOrbital(self.x, self.y, 15, 0.1, self.color, 2)
            )

        for p in self.particulas_orbitales[:]:
            p.actualizar()
            if p.life <= 0:
                self.particulas_orbitales.remove(p)

    def dibujar(self, superficie):
        if self.life > 0:
            for p in self.particulas_orbitales:
                p.dibujar(superficie)

            pulso = (math.sin(self.anim_time * 0.1) + 1) / 2
            radio = TAM_CELDA//2 + int(pulso * 4)

            glow_surf = pygame.Surface((radio*2 + 15, radio*2 + 15), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, 80), (radio + 7, radio + 7), radio + 7)
            superficie.blit(glow_surf, (self.x - radio - 7, self.y - radio - 7))

            pygame.draw.circle(superficie, self.color, (self.x, self.y), radio)
            pygame.draw.circle(superficie, BLANCO, (self.x, self.y), radio, 2)

            icono_surf = fuente_pequena.render(self.icono, True, BLANCO)
            superficie.blit(icono_surf, (self.x - icono_surf.get_width()//2,
                                        self.y - icono_surf.get_height()//2))

class ManzanaEspecial:
    def __init__(self, x, y, tipo):
        self.x, self.y = x, y
        self.tipo = tipo
        self.life = 180
        self.anim_time = 0
        self.particulas_orbitales = []

        if tipo == 'diamante':
            self.color = NEON_CYAN
            self.puntos = 5
            self.icono = 'D'
        elif tipo == 'estrella':
            self.color = NEON_AMARILLO
            self.puntos = 10
            self.icono = '★'

    def actualizar(self):
        self.life -= 1
        self.anim_time += 1

        if self.anim_time % 3 == 0:
            self.particulas_orbitales.append(
                ParticulaOrbital(self.x, self.y, 18, 0.15, self.color, 2)
            )

        for p in self.particulas_orbitales[:]:
            p.actualizar()
            if p.life <= 0:
                self.particulas_orbitales.remove(p)

    def dibujar(self, superficie):
        if self.life > 0:
            if self.life < 60 and (self.life // 5) % 2 == 0:
                return

            for p in self.particulas_orbitales:
                p.dibujar(superficie)

            pulso = (math.sin(self.anim_time * 0.15) + 1) / 2
            radio = TAM_CELDA//2 + int(pulso * 5)

            glow_surf = pygame.Surface((radio*2 + 20, radio*2 + 20), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, 100), (radio + 10, radio + 10), radio + 10)
            superficie.blit(glow_surf, (self.x - radio - 10, self.y - radio - 10))

            pygame.draw.circle(superficie, self.color, (self.x, self.y), radio)
            pygame.draw.circle(superficie, BLANCO, (self.x, self.y), radio, 2)

            icono_surf = fuente_pequena.render(self.icono, True, BLANCO)
            superficie.blit(icono_surf, (self.x - icono_surf.get_width()//2,
                                        self.y - icono_surf.get_height()//2))

class ParticulaFondo:
    def __init__(self):
        self.reset()
        self.y = random.randint(0, ALTO)

    def reset(self):
        self.x = random.randint(0, ANCHO)
        self.y = ALTO + 10
        self.size = random.uniform(1, 3)
        self.speed = random.uniform(0.5, 2)
        self.color = random.choice([NEON_CYAN, NEON_PURPURA, NEON_VERDE, NEON_AMARILLO])
        self.alpha = random.randint(80, 200)

    def actualizar(self):
        self.y -= self.speed
        self.x += math.sin(self.y * 0.02) * 0.5
        if self.y < -10:
            self.reset()

    def dibujar(self, superficie):
        s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        s.fill((*self.color, self.alpha))
        superficie.blit(s, (int(self.x - self.size), int(self.y - self.size)))

particulas_menu = [ParticulaFondo() for _ in range(80)]

def dibujar_fondo_menu(tick):
    for y in range(ALTO):
        ratio = y / ALTO
        color = (int(5 + ratio * 15), int(2 + ratio * 5), int(15 + ratio * 20))
        pygame.draw.line(pantalla, color, (0, y), (ANCHO, y))

    horizonte_y = ALTO // 2 + 40

    for i in range(20):
        t = i / 20
        y = int(horizonte_y + (ALTO - horizonte_y) * (t ** 1.8))
        alpha = int(40 + t * 60)
        color_linea = (NEON_PURPURA[0]//3, NEON_PURPURA[1]//4, NEON_PURPURA[2]//2)
        s = pygame.Surface((ANCHO, 1), pygame.SRCALPHA)
        s.fill((*color_linea, alpha))
        pantalla.blit(s, (0, y))

    centro_x = ANCHO // 2
    for i in range(-15, 16):
        offset = i * 60
        x_top = centro_x + offset // 8
        x_bottom = centro_x + offset * 2
        pygame.draw.line(pantalla, (NEON_PURPURA[0]//4, NEON_PURPURA[1]//5, NEON_PURPURA[2]//3),
                        (x_top, horizonte_y), (x_bottom, ALTO), 1)

    s_hor = pygame.Surface((ANCHO, 2), pygame.SRCALPHA)
    pulse_h = (math.sin(tick * 0.05) + 1) / 2
    alpha_h = int(100 + pulse_h * 100)
    s_hor.fill((NEON_CYAN[0], NEON_CYAN[1], NEON_CYAN[2], alpha_h))
    pantalla.blit(s_hor, (0, horizonte_y))

    sol_y = horizonte_y - 30
    sol_radio = 80 + int(math.sin(tick * 0.03) * 5)

    for i in range(5, 0, -1):
        glow_r = sol_radio + i * 15
        glow_surf = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (NEON_PURPURA[0], NEON_PURPURA[1], NEON_PURPURA[2], 20),
                          (glow_r, glow_r), glow_r)
        pantalla.blit(glow_surf, (ANCHO//2 - glow_r, sol_y - glow_r))

    for row in range(-sol_radio, sol_radio, 3):
        half_width = int(math.sqrt(max(0, sol_radio**2 - row**2)))
        if half_width > 0:
            ratio = (row + sol_radio) / (sol_radio * 2)
            color_sol = (int(255 * (1 - ratio * 0.3)), int(100 * (1 - ratio)), int(200 * ratio))
            pygame.draw.line(pantalla, color_sol,
                           (ANCHO//2 - half_width, sol_y + row),
                           (ANCHO//2 + half_width, sol_y + row), 2)

    for p in particulas_menu:
        p.actualizar()
        p.dibujar(pantalla)

    for i in range(3):
        radio_c = 100 + i * 80 + int(math.sin(tick * 0.04 + i) * 20)
        alpha_c = max(0, 40 - i * 10)
        circ_surf = pygame.Surface((radio_c*2, radio_c*2), pygame.SRCALPHA)
        pygame.draw.circle(circ_surf, (NEON_CYAN[0], NEON_CYAN[1], NEON_CYAN[2], alpha_c),
                          (radio_c, radio_c), radio_c, 2)
        pantalla.blit(circ_surf, (ANCHO//2 - radio_c, ALTO//2 - radio_c))

class ParticulaFondoJuego:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, ANCHO)
        self.y = random.randint(0, ALTO)
        self.size = random.uniform(1, 3)
        self.speed = random.uniform(0.3, 1.2)
        self.alpha = random.randint(80, 200)
        self.twinkle = random.uniform(0, math.pi * 2)

    def actualizar(self):
        self.y -= self.speed
        self.x += math.sin(self.y * 0.02) * 0.3
        self.twinkle += 0.08
        if self.y < -10:
            self.reset()

    def dibujar(self, superficie):
        alpha_actual = int(self.alpha * (0.5 + 0.5 * math.sin(self.twinkle)))
        s = pygame.Surface((int(self.size*3), int(self.size*3)), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, alpha_actual),
                          (int(self.size*1.5), int(self.size*1.5)), int(self.size))
        superficie.blit(s, (int(self.x - self.size*1.5), int(self.y - self.size*1.5)))

particulas_fondo_juego = [ParticulaFondoJuego() for _ in range(80)]

def dibujar_fondo_juego(tick):
    pantalla.fill(NEGRO)

    for p in particulas_fondo_juego:
        p.actualizar()
        p.dibujar(pantalla)

    pulso_grid = (math.sin(tick * 0.05) + 1) / 2
    alpha_grid = int(10 + pulso_grid * 8)

    for x in range(0, ANCHO, TAM_CELDA):
        s = pygame.Surface((1, ALTO), pygame.SRCALPHA)
        s.fill((30, 30, 40, alpha_grid))
        pantalla.blit(s, (x, 0))

    for y in range(0, ALTO, TAM_CELDA):
        s = pygame.Surface((ANCHO, 1), pygame.SRCALPHA)
        s.fill((30, 30, 40, alpha_grid))
        pantalla.blit(s, (0, y))

def dibujar_score_record(puntaje, record):
    score_texto = f"SCORE: {puntaje}"
    score_surf = fuente_texto.render(score_texto, True, NEON_VERDE)

    score_rect = pygame.Rect(15, 10, score_surf.get_width() + 20, score_surf.get_height() + 10)

    glow_surf = pygame.Surface((score_rect.width + 10, score_rect.height + 10), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf, (0, 255, 65, 60), glow_surf.get_rect(), border_radius=8)
    pantalla.blit(glow_surf, (score_rect.x - 5, score_rect.y - 5))

    pygame.draw.rect(pantalla, (0, 40, 20), score_rect, border_radius=6)
    pygame.draw.rect(pantalla, NEON_VERDE, score_rect, 2, border_radius=6)
    pantalla.blit(score_surf, (score_rect.x + 10, score_rect.y + 5))

    record_texto = f"RECORD: {record}"
    record_surf = fuente_pequena.render(record_texto, True, NEON_CYAN)

    record_rect = pygame.Rect(15, 55, record_surf.get_width() + 20, record_surf.get_height() + 10)

    glow_surf2 = pygame.Surface((record_rect.width + 10, record_rect.height + 10), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf2, (0, 255, 255, 60), glow_surf2.get_rect(), border_radius=8)
    pantalla.blit(glow_surf2, (record_rect.x - 5, record_rect.y - 5))

    pygame.draw.rect(pantalla, (0, 30, 40), record_rect, border_radius=6)
    pygame.draw.rect(pantalla, NEON_CYAN, record_rect, 2, border_radius=6)
    pantalla.blit(record_surf, (record_rect.x + 10, record_rect.y + 5))

def dibujar_texto_resplandor(texto, fuente, color, superficie, x, y, alineacion="center"):
    texto_glow = fuente.render(texto, True, color)
    glow_rect = texto_glow.get_rect()
    if alineacion == "center":
        glow_rect.center = (x, y)
    else:
        glow_rect.topleft = (x, y)

    for i in range(3, 0, -1):
        glow_surface = pygame.transform.scale(texto_glow,
            (texto_glow.get_width() + i*4, texto_glow.get_height() + i*4))
        glow_rect_scaled = glow_surface.get_rect(center=glow_rect.center)
        s = pygame.Surface(glow_surface.get_size(), pygame.SRCALPHA)
        s.fill((*color, 50))
        superficie.blit(s, glow_rect_scaled.topleft)

    superficie.blit(texto_glow, glow_rect.topleft)

def dibujar_segmento_serpiente(superficie, x, y, color, es_cabeza=False, indice=0, tick=0):
    rect = pygame.Rect(x, y, TAM_CELDA, TAM_CELDA)

    glow_size = 10 if es_cabeza else 6
    glow_rect = rect.inflate(glow_size, glow_size)
    s = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
    alpha_glow = 100 if es_cabeza else 60
    pygame.draw.rect(s, (*color, alpha_glow), s.get_rect(), border_radius=8)
    superficie.blit(s, glow_rect.topleft)

    if es_cabeza:
        pygame.draw.rect(superficie, color, rect, border_radius=6)
        highlight_rect = pygame.Rect(x + 2, y + 2, TAM_CELDA - 4, TAM_CELDA // 3)
        s = pygame.Surface(highlight_rect.size, pygame.SRCALPHA)
        s.fill((255, 255, 255, 80))
        superficie.blit(s, highlight_rect.topleft)
        pygame.draw.rect(superficie, (255, 255, 255, 150), rect, 2, border_radius=6)
    else:
        pulso = int(math.sin((tick + indice * 8) * 0.1) * 20)
        color_pulso = (color[0], min(255, color[1] + pulso), min(255, color[2] + pulso//2))
        pygame.draw.rect(superficie, color_pulso, rect, border_radius=5)
        pygame.draw.rect(superficie, (255, 255, 255, 80), rect, 1, border_radius=5)

def dibujar_manzana(superficie, x, y, tick):
    centro_x = x + TAM_CELDA // 2
    centro_y = y + TAM_CELDA // 2

    pulso = (math.sin(tick * 0.1) + 1) / 2
    radio = TAM_CELDA // 2 + int(pulso * 4)

    angulo_rot = tick * 0.05

    for i in range(3):
        ang = angulo_rot + i * (math.pi * 2 / 3)
        px = centro_x + math.cos(ang) * (radio + 5)
        py = centro_y + math.sin(ang) * (radio + 5)
        s = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*NEON_ROJO, 150), (2, 2), 2)
        superficie.blit(s, (int(px - 2), int(py - 2)))

    glow_surf = pygame.Surface((radio*2 + 15, radio*2 + 15), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (*NEON_ROJO, 80), (radio + 7, radio + 7), radio + 7)
    superficie.blit(glow_surf, (centro_x - radio - 7, centro_y - radio - 7))

    pygame.draw.circle(superficie, NEON_ROJO, (centro_x, centro_y), radio)

    brillo_surf = pygame.Surface((radio, radio//2), pygame.SRCALPHA)
    pygame.draw.ellipse(brillo_surf, (255, 255, 255, 100), brillo_surf.get_rect())
    superficie.blit(brillo_surf, (centro_x - radio//2, centro_y - radio//2))

    pygame.draw.circle(superficie, (255, 255, 255, 150), (centro_x, centro_y), radio, 2)

    pygame.draw.ellipse(superficie, NEON_VERDE,
                       (centro_x - 3, centro_y - radio - 2, 6, 4))

class Boton:
    def __init__(self, x, y, ancho, alto, texto, color_base):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_base = color_base
        self.color_hover = tuple(min(255, int(c * 1.4)) for c in color_base)
        self.color_actual = list(color_base)
        self.hover = False
        self.anim_time = 0

    def actualizar(self, eventos):
        pos_mouse = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(pos_mouse)
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and self.hover:
                return True
        return False

    def dibujar(self, superficie):
        self.anim_time += 1
        pulse = (math.sin(self.anim_time * 0.08) + 1) / 2

        target_color = self.color_hover if self.hover else self.color_base
        factor = 0.18 if self.hover else 0.08
        self.color_actual = [
            max(0, min(255, int(self.color_actual[i] + (target_color[i] - self.color_actual[i]) * factor)))
            for i in range(3)
        ]

        glow_size = 8 + int(pulse * 8)
        glow_rect = self.rect.inflate(glow_size * 2, glow_size * 2)
        glow_alpha = int(40 + pulse * 50)
        glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*self.color_actual, glow_alpha),
                         glow_surface.get_rect(), border_radius=14)
        superficie.blit(glow_surface, glow_rect.topleft)

        border_rect = self.rect.inflate(3, 3)
        border_surface = pygame.Surface(border_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(border_surface, (*self.color_actual, 220),
                         border_surface.get_rect(), border_radius=10, width=2)
        superficie.blit(border_surface, border_rect.topleft)

        base_color = tuple(max(0, c - 100) for c in self.color_actual)
        pygame.draw.rect(superficie, base_color, self.rect, border_radius=10)

        for i in range(self.rect.height):
            ratio = i / self.rect.height
            alpha = int(160 * (1 - ratio * 0.7))
            grad_rect = pygame.Rect(self.rect.x, self.rect.y + i, self.rect.width, 1)
            s = pygame.Surface((self.rect.width, 1), pygame.SRCALPHA)
            s.fill((*self.color_actual, alpha))
            superficie.blit(s, grad_rect.topleft)

        highlight_h = self.rect.height // 3
        for i in range(highlight_h):
            ratio = i / highlight_h
            alpha = int(60 * (1 - ratio))
            hl_rect = pygame.Rect(self.rect.x + 4, self.rect.y + i, self.rect.width - 8, 1)
            s = pygame.Surface((self.rect.width - 8, 1), pygame.SRCALPHA)
            s.fill((255, 255, 255, alpha))
            superficie.blit(s, hl_rect.topleft)

        inner_rect = self.rect.inflate(-2, -2)
        inner_surface = pygame.Surface(inner_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(inner_surface, (255, 255, 255, 100),
                         inner_surface.get_rect(), border_radius=9, width=1)
        superficie.blit(inner_surface, inner_rect.topleft)

        texto_sombra = fuente_pequena.render(self.texto, True, (0, 0, 0))
        texto_sombra_rect = texto_sombra.get_rect(center=self.rect.center)
        texto_sombra_rect.y += 2
        superficie.blit(texto_sombra, texto_sombra_rect.topleft)

        texto_surf = fuente_pequena.render(self.texto, True, (240, 240, 240))
        texto_rect = texto_surf.get_rect(center=self.rect.center)

        for offset in range(2, 0, -1):
            glow_text = pygame.transform.scale(texto_surf,
                (texto_surf.get_width() + offset*2, texto_surf.get_height() + offset*2))
            glow_rect_t = glow_text.get_rect(center=texto_rect.center)
            s = pygame.Surface(glow_text.get_size(), pygame.SRCALPHA)
            s.fill((*self.color_actual, 100))
            superficie.blit(s, glow_rect_t.topleft)

        superficie.blit(texto_surf, texto_rect.topleft)

def guardar_record(puntaje):
    try:
        with open("record.txt", "r") as f:
            record = int(f.read())
    except:
        record = 0
    if puntaje > record:
        with open("record.txt", "w") as f:
            f.write(str(puntaje))
        return puntaje
    return record

def obtener_record():
    try:
        with open("record.txt", "r") as f:
            return int(f.read())
    except:
        return 0

def dibujar_scanlines():
    for y in range(0, ALTO, 4):
        pygame.draw.line(pantalla, (0, 0, 0, 30), (0, y), (ANCHO, y))

def main():
    estado = "MENU"
    tick_global = 0
    pausado = False

    serpiente = [(100, 100), (80, 100), (60, 100)]
    direccion = (TAM_CELDA, 0)
    siguiente_direccion = (TAM_CELDA, 0)
    manzana = (random.randint(0, (ANCHO-TAM_CELDA)//TAM_CELDA)*TAM_CELDA,
               random.randint(0, (ALTO-TAM_CELDA)//TAM_CELDA)*TAM_CELDA)
    puntaje = 0
    tick_juego = 0
    fps_juego = FPS_JUEGO_INICIAL

    particulas = []
    estelas = []
    textos_flotantes = []
    power_ups = []
    manzanas_especiales = []
    shake = ScreenShake()

    escudo_activo = 0
    velocidad_activa = 0
    puntos_dobles = 0

    manzanas_comidas = 0
    manzana_especial_timer = 0
    power_up_timer = 0

    btn_jugar = Boton(ANCHO//2 - 100, 320, 200, 50, "JUGAR", NEON_VERDE)
    btn_salir = Boton(ANCHO//2 - 100, 400, 200, 50, "SALIR", NEON_ROJO)
    btn_reintentar = Boton(ANCHO//2 - 120, 350, 240, 50, "REINTENTAR", NEON_CYAN)
    btn_menu = Boton(ANCHO//2 - 120, 430, 240, 50, "MENÚ PRINCIPAL", NEON_PURPURA)

    def reset_juego():
        nonlocal serpiente, direccion, siguiente_direccion, manzana, puntaje, tick_juego
        nonlocal fps_juego, particulas, estelas, textos_flotantes, power_ups, manzanas_especiales
        nonlocal escudo_activo, velocidad_activa, puntos_dobles
        nonlocal manzanas_comidas, manzana_especial_timer, power_up_timer

        serpiente = [(100, 100), (80, 100), (60, 100)]
        direccion = (TAM_CELDA, 0)
        siguiente_direccion = (TAM_CELDA, 0)
        manzana = (random.randint(0, (ANCHO-TAM_CELDA)//TAM_CELDA)*TAM_CELDA,
                   random.randint(0, (ALTO-TAM_CELDA)//TAM_CELDA)*TAM_CELDA)
        puntaje = 0
        tick_juego = 0
        fps_juego = FPS_JUEGO_INICIAL
        particulas = []
        estelas = []
        textos_flotantes = []
        power_ups = []
        manzanas_especiales = []
        escudo_activo = 0
        velocidad_activa = 0
        puntos_dobles = 0
        manzanas_comidas = 0
        manzana_especial_timer = 0
        power_up_timer = 0

    def crear_explosion(x, y, color, cantidad=20):
        for _ in range(cantidad):
            angulo = random.uniform(0, math.pi * 2)
            velocidad = random.uniform(2, 6)
            vx = math.cos(angulo) * velocidad
            vy = math.sin(angulo) * velocidad
            size = random.randint(3, 7)
            life = random.randint(30, 50)
            particulas.append(Particula(x, y, color, vx, vy, size, life))

    def crear_estela(x, y, color):
        estelas.append(Estela(x, y, color, TAM_CELDA))

    while True:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        tick_global += 1
        shake_x, shake_y = shake.actualizar()

        pantalla.fill((10, 10, 15))

        if estado == "MENU":
            dibujar_fondo_menu(tick_global)

            titulo_y = 140 + int(math.sin(tick_global * 0.04) * 8)
            dibujar_texto_resplandor("NEON SNAKE", fuente_titulo, NEON_CYAN, pantalla, ANCHO//2, titulo_y)
            dibujar_texto_resplandor("ULTRA GAMER EDITION", fuente_pequena, NEON_PURPURA, pantalla, ANCHO//2, titulo_y + 60)

            if btn_jugar.actualizar(eventos):
                estado = "JUGANDO"
                reset_juego()

            if btn_salir.actualizar(eventos):
                pygame.quit()
                sys.exit()

            btn_jugar.dibujar(pantalla)
            btn_salir.dibujar(pantalla)

        elif estado == "JUGANDO":
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_p]:
                pausado = not pausado
                pygame.time.wait(200)

            if pausado:
                dibujar_fondo_juego(tick_global)
                for i, segmento in enumerate(serpiente):
                    dibujar_segmento_serpiente(pantalla, segmento[0], segmento[1],
                                             NEON_VERDE if i == 0 else (0, 200, 50),
                                             i == 0, i, tick_global)

                dibujar_manzana(pantalla, manzana[0], manzana[1], tick_global)

                s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
                s.fill((0, 0, 0, 150))
                pantalla.blit(s, (0, 0))
                dibujar_texto_resplandor("PAUSA", fuente_titulo, NEON_CYAN,
                                       pantalla, ANCHO//2, ALTO//2 - 30)
                dibujar_texto_resplandor("Presiona P para continuar", fuente_pequena, BLANCO,
                                       pantalla, ANCHO//2, ALTO//2 + 30)
            else:
                dibujar_fondo_juego(tick_global)

                dibujar_score_record(puntaje, obtener_record())

                if teclas[pygame.K_UP] and direccion != (0, TAM_CELDA):
                    siguiente_direccion = (0, -TAM_CELDA)
                elif teclas[pygame.K_DOWN] and direccion != (0, -TAM_CELDA):
                    siguiente_direccion = (0, TAM_CELDA)
                elif teclas[pygame.K_LEFT] and direccion != (TAM_CELDA, 0):
                    siguiente_direccion = (-TAM_CELDA, 0)
                elif teclas[pygame.K_RIGHT] and direccion != (-TAM_CELDA, 0):
                    siguiente_direccion = (TAM_CELDA, 0)

                tick_juego += 1
                if tick_juego >= (FPS // fps_juego):
                    tick_juego = 0
                    direccion = siguiente_direccion
                    nueva_cabeza = (serpiente[0][0] + direccion[0], serpiente[0][1] + direccion[1])

                    crear_estela(serpiente[0][0] + TAM_CELDA//2,
                               serpiente[0][1] + TAM_CELDA//2, NEON_VERDE)

                    murio = False
                    if (nueva_cabeza[0] < 0 or nueva_cabeza[0] >= ANCHO or
                        nueva_cabeza[1] < 0 or nueva_cabeza[1] >= ALTO):
                        if escudo_activo <= 0:
                            murio = True
                        else:
                            if nueva_cabeza[0] < 0: nueva_cabeza = (0, nueva_cabeza[1])
                            elif nueva_cabeza[0] >= ANCHO: nueva_cabeza = (ANCHO-TAM_CELDA, nueva_cabeza[1])
                            if nueva_cabeza[1] < 0: nueva_cabeza = (nueva_cabeza[0], 0)
                            elif nueva_cabeza[1] >= ALTO: nueva_cabeza = (nueva_cabeza[0], ALTO-TAM_CELDA)

                    if nueva_cabeza in serpiente[:-1]:
                        if escudo_activo <= 0:
                            murio = True

                    if murio:
                        estado = "GAMEOVER"
                        if sonido_morir: sonido_morir.play()
                        guardar_record(puntaje)
                        shake.activar(10, 20)
                        crear_explosion(serpiente[0][0] + TAM_CELDA//2,
                                      serpiente[0][1] + TAM_CELDA//2, NEON_ROJO, 40)
                    else:
                        serpiente.insert(0, nueva_cabeza)

                        if nueva_cabeza == manzana:
                            puntos_ganados = 1 * (2 if puntos_dobles > 0 else 1)
                            puntaje += puntos_ganados
                            manzanas_comidas += 1
                            if sonido_comer: sonido_comer.play()

                            crear_explosion(manzana[0] + TAM_CELDA//2,
                                          manzana[1] + TAM_CELDA//2, NEON_ROJO, 30)

                            while True:
                                manzana = (random.randint(0, (ANCHO-TAM_CELDA)//TAM_CELDA)*TAM_CELDA,
                                           random.randint(0, (ALTO-TAM_CELDA)//TAM_CELDA)*TAM_CELDA)
                                if manzana not in serpiente:
                                    break

                            power_up_timer += 1
                            if power_up_timer >= 10:
                                power_up_timer = 0
                                tipo = random.choice(['escudo', 'velocidad', 'puntos_dobles'])
                                px = random.randint(50, ANCHO-50)
                                py = random.randint(50, ALTO-50)
                                power_ups.append(PowerUp(px, py, tipo))

                            manzana_especial_timer += 1
                            if manzana_especial_timer >= 15:
                                manzana_especial_timer = 0
                                tipo = random.choice(['diamante', 'estrella'])
                                mx = random.randint(50, ANCHO-50)
                                my = random.randint(50, ALTO-50)
                                manzanas_especiales.append(ManzanaEspecial(mx, my, tipo))
                        else:
                            serpiente.pop()

                        for pu in power_ups[:]:
                            dist = math.sqrt((nueva_cabeza[0] + TAM_CELDA//2 - pu.x)**2 +
                                           (nueva_cabeza[1] + TAM_CELDA//2 - pu.y)**2)
                            if dist < TAM_CELDA:
                                if pu.tipo == 'escudo':
                                    escudo_activo = 300
                                    textos_flotantes.append(TextoFlotante(
                                        "SHIELD!", pu.x, pu.y, NEON_CYAN, 32
                                    ))
                                elif pu.tipo == 'velocidad':
                                    velocidad_activa = 300
                                    fps_juego = min(30, fps_juego + 5)
                                    textos_flotantes.append(TextoFlotante(
                                        "SPEED!", pu.x, pu.y, NEON_AMARILLO, 32
                                    ))
                                elif pu.tipo == 'puntos_dobles':
                                    puntos_dobles = 600
                                    textos_flotantes.append(TextoFlotante(
                                        "2X POINTS!", pu.x, pu.y, NEON_PURPURA, 32
                                    ))

                                if sonido_power: sonido_power.play()
                                crear_explosion(pu.x, pu.y, pu.color, 20)
                                power_ups.remove(pu)

                        for me in manzanas_especiales[:]:
                            dist = math.sqrt((nueva_cabeza[0] + TAM_CELDA//2 - me.x)**2 +
                                           (nueva_cabeza[1] + TAM_CELDA//2 - me.y)**2)
                            if dist < TAM_CELDA:
                                puntos_ganados = me.puntos * (2 if puntos_dobles > 0 else 1)
                                puntaje += puntos_ganados
                                if sonido_power: sonido_power.play()
                                crear_explosion(me.x, me.y, me.color, 30)
                                manzanas_especiales.remove(me)

                if escudo_activo > 0: escudo_activo -= 1
                if velocidad_activa > 0:
                    velocidad_activa -= 1
                    if velocidad_activa == 0:
                        fps_juego = max(FPS_JUEGO_INICIAL, fps_juego - 5)
                if puntos_dobles > 0: puntos_dobles -= 1

                for pu in power_ups[:]:
                    pu.actualizar()
                    if pu.life <= 0:
                        power_ups.remove(pu)

                for me in manzanas_especiales[:]:
                    me.actualizar()
                    if me.life <= 0:
                        manzanas_especiales.remove(me)

                for p in particulas[:]:
                    p.actualizar()
                    if p.life <= 0:
                        particulas.remove(p)

                for e in estelas[:]:
                    e.actualizar()
                    if e.life <= 0:
                        estelas.remove(e)

                for t in textos_flotantes[:]:
                    t.actualizar()
                    if t.life <= 0:
                        textos_flotantes.remove(t)

                for e in estelas:
                    e.dibujar(pantalla)

                dibujar_manzana(pantalla, manzana[0], manzana[1], tick_global)

                for pu in power_ups:
                    pu.dibujar(pantalla)

                for me in manzanas_especiales:
                    me.dibujar(pantalla)

                for i, segmento in enumerate(serpiente):
                    if i == 0:
                        dibujar_segmento_serpiente(pantalla, segmento[0], segmento[1],
                                                 NEON_VERDE, True, i, tick_global)

                        if direccion == (TAM_CELDA, 0):
                            ojo1 = (segmento[0] + TAM_CELDA - 6, segmento[1] + 5)
                            ojo2 = (segmento[0] + TAM_CELDA - 6, segmento[1] + TAM_CELDA - 7)
                        elif direccion == (-TAM_CELDA, 0):
                            ojo1 = (segmento[0] + 4, segmento[1] + 5)
                            ojo2 = (segmento[0] + 4, segmento[1] + TAM_CELDA - 7)
                        elif direccion == (0, -TAM_CELDA):
                            ojo1 = (segmento[0] + 5, segmento[1] + 4)
                            ojo2 = (segmento[0] + TAM_CELDA - 7, segmento[1] + 4)
                        else:
                            ojo1 = (segmento[0] + 5, segmento[1] + TAM_CELDA - 6)
                            ojo2 = (segmento[0] + TAM_CELDA - 7, segmento[1] + TAM_CELDA - 6)

                        pygame.draw.circle(pantalla, BLANCO, ojo1, 4)
                        pygame.draw.circle(pantalla, BLANCO, ojo2, 4)
                        pygame.draw.circle(pantalla, (0, 0, 0), ojo1, 2)
                        pygame.draw.circle(pantalla, (0, 0, 0), ojo2, 2)
                        pygame.draw.circle(pantalla, (255, 255, 255), (ojo1[0]+1, ojo1[1]-1), 1)
                        pygame.draw.circle(pantalla, (255, 255, 255), (ojo2[0]+1, ojo2[1]-1), 1)

                        if escudo_activo > 0:
                            glow_surf = pygame.Surface((TAM_CELDA + 12, TAM_CELDA + 12), pygame.SRCALPHA)
                            pygame.draw.rect(glow_surf, (*NEON_CYAN, 100), glow_surf.get_rect(), border_radius=8)
                            pantalla.blit(glow_surf, (segmento[0] - 6, segmento[1] - 6))
                    else:
                        color_base = (0, 200, 50)
                        ratio = i / len(serpiente)
                        color_seg = (
                            int(color_base[0] * (1 - ratio)),
                            int(color_base[1] * (1 - ratio * 0.3)),
                            int(color_base[2] * (1 - ratio * 0.5))
                        )

                        dibujar_segmento_serpiente(pantalla, segmento[0], segmento[1],
                                                 color_seg, False, i, tick_global)

                for p in particulas:
                    p.dibujar(pantalla)

                for t in textos_flotantes:
                    t.dibujar(pantalla)

        elif estado == "GAMEOVER":
            dibujar_fondo_juego(tick_global)

            for p in particulas[:]:
                p.actualizar()
                if p.life <= 0:
                    particulas.remove(p)

            for p in particulas:
                p.dibujar(pantalla)

            s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            pantalla.blit(s, (0, 0))

            game_over_texto = "GAME OVER"
            game_over_surf = fuente_titulo.render(game_over_texto, True, NEON_ROJO)
            game_over_rect = game_over_surf.get_rect(center=(ANCHO//2, ALTO//2 - 100))

            for i in range(3, 0, -1):
                glow = pygame.transform.scale(game_over_surf,
                    (game_over_surf.get_width() + i*6, game_over_surf.get_height() + i*6))
                glow_rect = glow.get_rect(center=game_over_rect.center)
                glow_s = pygame.Surface(glow.get_size(), pygame.SRCALPHA)
                pygame.draw.rect(glow_s, (255, 0, 85, 40), glow_s.get_rect(), border_radius=10)
                pantalla.blit(glow_s, glow_rect.topleft)

            pantalla.blit(game_over_surf, game_over_rect.topleft)

            puntaje_texto = f"PUNTAJE: {puntaje}"
            puntaje_surf = fuente_texto.render(puntaje_texto, True, BLANCO)
            puntaje_rect = puntaje_surf.get_rect(center=(ANCHO//2, ALTO//2 - 30))
            pantalla.blit(puntaje_surf, puntaje_rect.topleft)

            record_texto = f"RECORD: {obtener_record()}"
            record_surf = fuente_pequena.render(record_texto, True, NEON_CYAN)
            record_rect = record_surf.get_rect(center=(ANCHO//2, ALTO//2 + 10))
            pantalla.blit(record_surf, record_rect.topleft)

            btn_reintentar.rect.center = (ANCHO//2, ALTO//2 + 80)
            btn_menu.rect.center = (ANCHO//2, ALTO//2 + 150)

            if btn_reintentar.actualizar(eventos):
                estado = "JUGANDO"
                reset_juego()

            if btn_menu.actualizar(eventos):
                estado = "MENU"

            btn_reintentar.dibujar(pantalla)
            btn_menu.dibujar(pantalla)

        dibujar_scanlines()
        pygame.display.flip()
        reloj.tick(FPS)

if __name__ == "__main__":
    main()
