import pygame
import random
import sys
import math
import numpy as np

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

CELL = 30
COLS, ROWS = 10, 20
PANEL_W = 250
WIDTH = COLS * CELL + PANEL_W
HEIGHT = ROWS * CELL
FPS = 60
LINEAS_OBJETIVO = 30

C = {
    'bg': (0, 0, 0),
    'grid': (20, 20, 30),
    'grid_light': (40, 40, 60),
    'I': (0, 240, 240), 'I_light': (100, 255, 255), 'I_dark': (0, 180, 180),
    'O': (240, 240, 0), 'O_light': (255, 255, 100), 'O_dark': (180, 180, 0),
    'T': (160, 0, 240), 'T_light': (200, 100, 255), 'T_dark': (120, 0, 180),
    'S': (0, 240, 0), 'S_light': (100, 255, 100), 'S_dark': (0, 180, 0),
    'Z': (240, 0, 0), 'Z_light': (255, 100, 100), 'Z_dark': (180, 0, 0),
    'J': (0, 0, 240), 'J_light': (100, 100, 255), 'J_dark': (0, 0, 180),
    'L': (240, 160, 0), 'L_light': (255, 200, 100), 'L_dark': (180, 120, 0),
    'ghost': (80, 80, 100),
    'text': (255, 255, 255),
    'gold': (255, 215, 0),
    'cyan': (0, 240, 240),
    'purple': (160, 0, 240),
    'green': (0, 240, 0),
    'red': (240, 0, 0),
    'white': (255, 255, 255),
    'orange': (240, 160, 0),
    'dark': (10, 10, 15),
    'btn_bg': (25, 25, 35),
    'btn_bg_hover': (45, 45, 60)
}

SHAPES = {
    'I': [[1,1,1,1]],
    'O': [[1,1],[1,1]],
    'T': [[0,1,0],[1,1,1]],
    'S': [[0,1,1],[1,1,0]],
    'Z': [[1,1,0],[0,1,1]],
    'J': [[1,0,0],[1,1,1]],
    'L': [[0,0,1],[1,1,1]]
}

pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TETRIS - GAMER EDITION")
reloj = pygame.time.Clock()

try:
    f_titulo = pygame.font.SysFont("consolas", 36, bold=True)
    f_txt = pygame.font.SysFont("consolas", 20, bold=True)
    f_btn = pygame.font.SysFont("consolas", 22, bold=True)
    f_pequena = pygame.font.SysFont("consolas", 16)
    f_epica = pygame.font.SysFont("impact", 48, bold=True)
except:
    f_titulo = pygame.font.Font(None, 36)
    f_txt = pygame.font.Font(None, 20)
    f_btn = pygame.font.Font(None, 22)
    f_pequena = pygame.font.Font(None, 16)
    f_epica = pygame.font.Font(None, 48)

class SoundGenerator:
    def __init__(self):
        self.sample_rate = 44100

    def generate_beep(self, frequency=440, duration=0.1, volume=0.3, wave_type='square'):
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)

        if wave_type == 'square':
            audio = np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == 'sine':
            audio = np.sin(2 * np.pi * frequency * t)
        else:
            audio = np.sin(2 * np.pi * frequency * t)

        fade_length = samples // 10
        if fade_length > 0 and samples > fade_length:
            fade_out = np.linspace(1, 0, fade_length)
            audio[-fade_length:] = audio[-fade_length:] * fade_out

        audio *= volume
        audio_stereo = np.column_stack((audio, audio))
        audio_int16 = (audio_stereo * 32767).astype(np.int16)

        return pygame.mixer.Sound(buffer=audio_int16.tobytes())

sound_gen = SoundGenerator()
sonido_move = sound_gen.generate_beep(200, 0.05, 0.2, 'square')
sonido_rotate = sound_gen.generate_beep(300, 0.08, 0.25, 'square')
sonido_drop = sound_gen.generate_beep(150, 0.1, 0.3, 'square')
sonido_hard_drop = sound_gen.generate_beep(100, 0.15, 0.4, 'square')
sonido_line = sound_gen.generate_beep(600, 0.2, 0.35, 'sine')
sonido_tetris = sound_gen.generate_beep(800, 0.3, 0.4, 'sine')
sonido_gameover = sound_gen.generate_beep(200, 0.5, 0.3, 'square')

class Particula:
    def __init__(self, x, y, color, vx, vy, size, life):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.size = size
        self.life = life
        self.max_life = life

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size *= 0.98

    def dibujar(self, superficie):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            superficie.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class TrailDrop:
    def __init__(self, x, y, color, color_light):
        self.x = x
        self.y = y
        self.color = color
        self.color_light = color_light
        self.life = 20
        self.max_life = 20

    def actualizar(self):
        self.life -= 1

    def dibujar(self, superficie):
        if self.life > 0:
            alpha = int(180 * (self.life / self.max_life))
            rect = pygame.Rect(self.x + 2, self.y + 2, CELL - 4, CELL - 4)
            s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
            pygame.draw.rect(s, (*self.color, alpha), s.get_rect(), border_radius=3)
            superficie.blit(s, rect.topleft)

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

class TextoFlotante:
    def __init__(self, texto, x, y, color, size=48, epico=False):
        self.texto = texto
        self.x = x
        self.y = y
        self.color = color
        self.life = 90 if epico else 60
        self.max_life = self.life
        self.size = size
        self.epico = epico
        self.scale = 2.0 if epico else 1.5

    def actualizar(self):
        self.life -= 1
        self.y -= 1.5 if self.epico else 1
        self.scale = max(1.0, self.scale - 0.05)

    def dibujar(self, superficie):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            fuente = f_epica if self.epico else pygame.font.SysFont("impact", self.size, bold=True)
            texto_surf = fuente.render(self.texto, True, self.color)

            if self.scale > 1.0:
                nuevo_ancho = int(texto_surf.get_width() * self.scale)
                nuevo_alto = int(texto_surf.get_height() * self.scale)
                texto_surf = pygame.transform.scale(texto_surf, (nuevo_ancho, nuevo_alto))

            s = pygame.Surface(texto_surf.get_size(), pygame.SRCALPHA)
            glow_size = 6 if self.epico else 3
            for i in range(glow_size, 0, -1):
                glow = pygame.transform.scale(texto_surf,
                    (texto_surf.get_width() + i*4, texto_surf.get_height() + i*4))
                glow_rect = glow.get_rect(center=(s.get_width()//2, s.get_height()//2))
                glow_s = pygame.Surface(glow.get_size(), pygame.SRCALPHA)
                glow_s.fill((*self.color, alpha // 3))
                s.blit(glow_s, glow_rect.topleft)

            s.blit(texto_surf, (s.get_width()//2 - texto_surf.get_width()//2,
                               s.get_height()//2 - texto_surf.get_height()//2))
            superficie.blit(s, (int(self.x - s.get_width()//2), int(self.y - s.get_height()//2)))

class ParticulaFondo:
    def __init__(self):
        self.reset()
        self.y = random.randint(0, HEIGHT)

    def reset(self):
        self.x = random.randint(0, COLS * CELL)
        self.y = HEIGHT + 10
        self.size = random.uniform(1, 3)
        self.speed = random.uniform(0.5, 2)
        self.color = random.choice([C['cyan'], C['purple'], C['green'], C['gold']])
        self.alpha = random.randint(30, 80)

    def actualizar(self):
        self.y -= self.speed
        if self.y < -10:
            self.reset()

    def dibujar(self, superficie):
        s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        s.fill((*self.color, self.alpha))
        superficie.blit(s, (int(self.x - self.size), int(self.y - self.size)))

particulas_fondo = [ParticulaFondo() for _ in range(30)]

def dibujar_fondo():
    pantalla.fill(C['bg'])

    for x in range(0, COLS * CELL, CELL):
        pygame.draw.line(pantalla, C['grid'], (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(pantalla, C['grid'], (0, y), (COLS * CELL, y), 1)

    for p in particulas_fondo:
        p.actualizar()
        p.dibujar(pantalla)

def dibujar_bloque_3d(superficie, x, y, color, color_light, color_dark, size=CELL):
    rect = pygame.Rect(x + 1, y + 1, size - 2, size - 2)

    pygame.draw.rect(superficie, color, rect, border_radius=3)

    pygame.draw.line(superficie, color_light, (x + 2, y + 2), (x + size - 3, y + 2), 2)
    pygame.draw.line(superficie, color_light, (x + 2, y + 2), (x + 2, y + size - 3), 2)

    pygame.draw.line(superficie, color_dark, (x + 2, y + size - 3), (x + size - 3, y + size - 3), 2)
    pygame.draw.line(superficie, color_dark, (x + size - 3, y + 2), (x + size - 3, y + size - 3), 2)

    brillo_rect = pygame.Rect(x + 4, y + 4, size - 10, size - 10)
    if brillo_rect.width > 0 and brillo_rect.height > 0:
        pygame.draw.rect(superficie, (*color_light, 60), brillo_rect, border_radius=2)

class Boton:
    def __init__(self, x, y, ancho, alto, texto, color_texto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_texto = color_texto
        self.color_fondo = list(C['btn_bg'])
        self.color_fondo_target = list(C['btn_bg'])
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

        # Cambiar color de fondo según hover (sin borde)
        if self.hover:
            self.color_fondo_target = list(C['btn_bg_hover'])
        else:
            self.color_fondo_target = list(C['btn_bg'])

        factor = 0.15
        self.color_fondo = [
            max(0, min(255, int(self.color_fondo[i] + (self.color_fondo_target[i] - self.color_fondo[i]) * factor)))
            for i in range(3)
        ]

        # Solo fondo del botón (sin borde/contorno)
        pygame.draw.rect(superficie, tuple(self.color_fondo), self.rect, border_radius=6)

        # Texto
        texto_surf = f_btn.render(self.texto, True, self.color_texto)
        texto_rect = texto_surf.get_rect(center=self.rect.center)
        superficie.blit(texto_surf, texto_rect.topleft)

class Pieza:
    def __init__(self, tipo, x=None, y=None):
        self.tipo = tipo
        self.forma = [fila[:] for fila in SHAPES[tipo]]
        self.x = x if x is not None else COLS//2 - len(self.forma[0])//2
        self.y = y if y is not None else 0
        self.color = C[tipo]
        self.color_light = C[tipo + '_light']
        self.color_dark = C[tipo + '_dark']

    def rotar(self):
        return [list(fila) for fila in zip(*self.forma[::-1])]

    def clonar(self):
        return Pieza(self.tipo, self.x, self.y)

class TetrisGame:
    def __init__(self):
        self.reset()
        self.particulas = []
        self.trails = []
        self.textos_flotantes = []
        self.shake = ScreenShake()
        self.tick_anim = 0

    def reset(self):
        self.grid = [[None]*COLS for _ in range(ROWS)]
        self.bolsa = []
        self.actual = self._next_piece()
        self.siguiente = self._next_piece()
        self.puntaje, self.lineas, self.nivel = 0, 0, 1
        self.estado = "menu"
        self.drop_timer = 0
        self.drop_delay = 800
        self.confeti = []
        self.particulas = []
        self.trails = []
        self.textos_flotantes = []
        self.tetris_count = 0

    def _next_piece(self):
        if not self.bolsa:
            self.bolsa = list(SHAPES.keys())
            random.shuffle(self.bolsa)
        tipo = self.bolsa.pop()
        return Pieza(tipo)

    def _colision(self, pieza, dx=0, dy=0):
        for r, fila in enumerate(pieza.forma):
            for c, val in enumerate(fila):
                if val:
                    nx, ny = pieza.x + c + dx, pieza.y + r + dy
                    if nx < 0 or nx >= COLS or ny >= ROWS or (ny >= 0 and self.grid[ny][nx]):
                        return True
        return False

    def _fijar_pieza(self):
        sonido_drop.play()

        for r, fila in enumerate(self.actual.forma):
            for c, val in enumerate(fila):
                if val:
                    if self.actual.y + r < 0:
                        self.estado = "gameover"
                        sonido_gameover.play()
                        return
                    self.grid[self.actual.y + r][self.actual.x + c] = (
                        self.actual.color, self.actual.color_light, self.actual.color_dark
                    )

        self._crear_particulas_fijacion()
        self._limpiar_lineas()
        self.actual = self.siguiente
        self.siguiente = self._next_piece()
        if self._colision(self.actual):
            self.estado = "gameover"
            sonido_gameover.play()

    def _crear_particulas_fijacion(self):
        for r, fila in enumerate(self.actual.forma):
            for c, val in enumerate(fila):
                if val:
                    x = (self.actual.x + c) * CELL + CELL//2
                    y = (self.actual.y + r) * CELL + CELL//2
                    for _ in range(5):
                        vx = random.uniform(-3, 3)
                        vy = random.uniform(-3, 1)
                        self.particulas.append(Particula(x, y, self.actual.color, vx, vy, random.randint(2, 4), 25))

    def _limpiar_lineas(self):
        lineas_limpias = 0
        for i in range(ROWS-1, -1, -1):
            if all(self.grid[i]):
                for c in range(COLS):
                    x = c * CELL + CELL//2
                    y = i * CELL + CELL//2
                    for _ in range(8):
                        vx = random.uniform(-4, 4)
                        vy = random.uniform(-5, -1)
                        self.particulas.append(Particula(x, y, C['gold'], vx, vy, random.randint(3, 6), 35))

                self.grid.pop(i)
                self.grid.insert(0, [None]*COLS)
                lineas_limpias += 1

        if lineas_limpias > 0:
            pts = {1:100, 2:300, 3:500, 4:800}
            puntos_ganados = pts.get(lineas_limpias, 0) * self.nivel
            self.puntaje += puntos_ganados
            self.lineas += lineas_limpias
            self.nivel = self.lineas // 10 + 1
            self.drop_delay = max(50, 800 - (self.nivel-1)*60)

            if lineas_limpias == 4:
                sonido_tetris.play()
                self.tetris_count += 1
                self.textos_flotantes.append(TextoFlotante("TETRIS!", COLS * CELL // 2, HEIGHT // 2, C['gold'], 64, epico=True))
            else:
                sonido_line.play()

            self.shake.activar(intensidad=lineas_limpias * 2, duracion=10)

            if self.lineas >= LINEAS_OBJETIVO:
                self.estado = "victoria"
                self._generar_confeti()

    def _generar_confeti(self):
        self.confeti = []
        colores = [C['cyan'], C['green'], C['purple'], C['gold'], C['red']]
        for _ in range(150):
            self.confeti.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(-HEIGHT, 0),
                'r': random.randint(3, 6),
                'c': random.choice(colores),
                'vy': random.uniform(3, 6),
                'vx': random.uniform(-2, 2)
            })

    def _ghost(self):
        g = self.actual.clonar()
        while not self._colision(g, dy=1):
            g.y += 1
        return g

    def mover(self, dx, dy):
        if self.estado != "jugando":
            return
        if not self._colision(self.actual, dx, dy):
            self.actual.x += dx
            self.actual.y += dy
            if dy == 0:
                sonido_move.play()
                self.drop_timer = 0

    def rotar_pieza(self):
        if self.estado != "jugando":
            return
        original = [fila[:] for fila in self.actual.forma]
        self.actual.forma = self.actual.rotar()
        for dx in [0, -1, 1, -2, 2]:
            if not self._colision(self.actual, dx):
                self.actual.x += dx
                sonido_rotate.play()
                return
        self.actual.forma = original

    def hard_drop(self):
        if self.estado != "jugando":
            return

        while not self._colision(self.actual, dy=1):
            for r, fila in enumerate(self.actual.forma):
                for c, val in enumerate(fila):
                    if val:
                        x = (self.actual.x + c) * CELL
                        y = (self.actual.y + r) * CELL
                        self.trails.append(TrailDrop(x, y, self.actual.color, self.actual.color_light))

            self.actual.y += 1
            self.drop_timer = 0

        self.shake.activar(intensidad=6, duracion=8)
        sonido_hard_drop.play()
        self.puntaje += 2
        self._fijar_pieza()

    def actualizar(self, dt):
        self.tick_anim += 1

        for p in self.particulas[:]:
            p.actualizar()
            if p.life <= 0:
                self.particulas.remove(p)

        for t in self.trails[:]:
            t.actualizar()
            if t.life <= 0:
                self.trails.remove(t)

        for t in self.textos_flotantes[:]:
            t.actualizar()
            if t.life <= 0:
                self.textos_flotantes.remove(t)

        self.shake.actualizar()

        if self.estado == "jugando":
            self.drop_timer += dt
            if self.drop_timer >= self.drop_delay:
                self.drop_timer = 0
                if not self._colision(self.actual, dy=1):
                    self.actual.y += 1
                else:
                    self._fijar_pieza()

        if self.estado == "victoria":
            for c in self.confeti:
                c['x'] += c['vx']
                c['y'] += c['vy']
                c['vx'] *= 0.99
                if c['y'] > HEIGHT:
                    c['y'] = -10
                    c['x'] = random.randint(0, COLS * CELL)

    def dibujar(self):
        shake_x, shake_y = self.shake.actualizar()

        dibujar_fondo()

        for t in self.trails:
            t.dibujar(pantalla)

        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c]:
                    color, color_light, color_dark = self.grid[r][c]
                    dibujar_bloque_3d(pantalla, c*CELL, r*CELL, color, color_light, color_dark)

        if self.estado == "jugando":
            g = self._ghost()
            for r, fila in enumerate(g.forma):
                for c, val in enumerate(fila):
                    if val:
                        rect_ghost = pygame.Rect((g.x + c) * CELL+2, (g.y + r) * CELL+2, CELL-4, CELL-4)
                        pygame.draw.rect(pantalla, C['ghost'], rect_ghost, 2, border_radius=2)

        if self.estado in ("jugando", "pausado", "gameover", "victoria"):
            for r, fila in enumerate(self.actual.forma):
                for c, val in enumerate(fila):
                    if val:
                        dibujar_bloque_3d(pantalla,
                            (self.actual.x + c) * CELL,
                            (self.actual.y + r) * CELL,
                            self.actual.color,
                            self.actual.color_light,
                            self.actual.color_dark)

        for p in self.particulas:
            p.dibujar(pantalla)

        for t in self.textos_flotantes:
            t.dibujar(pantalla)

        self._dibujar_panel()

        if self.estado == "victoria":
            for c in self.confeti:
                pygame.draw.circle(pantalla, c['c'], (int(c['x']), int(c['y'])), c['r'])

        if self.estado == "menu":
            self._dibujar_menu()
        elif self.estado == "pausado":
            self._overlay("PAUSA", "Presiona P para continuar", False)
        elif self.estado == "gameover":
            self._overlay("GAME OVER", f"Líneas: {self.lineas} | Puntos: {self.puntaje:,}", True)
        elif self.estado == "victoria":
            self._overlay("¡VICTORIA!", f"Objetivo: {LINEAS_OBJETIVO} líneas completadas", True)

        pygame.display.flip()

    def _dibujar_menu(self):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        pantalla.blit(s, (0, 0))

        titulo_surf = f_titulo.render("TETRIS", True, C['cyan'])
        titulo_rect = titulo_surf.get_rect(center=(WIDTH//2, 180))
        pantalla.blit(titulo_surf, titulo_rect.topleft)

        sub_surf = f_pequena.render("GAMER EDITION", True, C['purple'])
        sub_rect = sub_surf.get_rect(center=(WIDTH//2, 230))
        pantalla.blit(sub_surf, sub_rect.topleft)

        btn_jugar.dibujar(pantalla)
        btn_salir.dibujar(pantalla)

        y = 450
        controles = [("← →", "Mover"), ("↑", "Rotar"), ("↓", "Caída suave"), ("ESPACIO", "Caída dura")]
        for tecla, accion in controles:
            pantalla.blit(f_pequena.render(f"{tecla:10} {accion}", True, (150, 150, 150)), (WIDTH//2 - 80, y))
            y += 25

    def _dibujar_panel(self):
        x = COLS*CELL + 15
        y = 20

        pygame.draw.rect(pantalla, C['gold'], (x, y, 200, 28), border_radius=4)
        titulo_surf = f_txt.render("ESTADÍSTICAS", True, C['dark'])
        pantalla.blit(titulo_surf, (x + 45, y + 4))
        y += 40

        stats = [
            ("NIVEL", self.nivel, C['cyan']),
            ("LÍNEAS", self.lineas, C['green']),
            ("PUNTOS", f"{self.puntaje:,}", C['gold']),
            ("TETRIS", f"{self.tetris_count}", C['purple'])
        ]

        for titulo, valor, color in stats:
            pantalla.blit(f_pequena.render(titulo, True, (180, 180, 180)), (x, y))
            texto_valor = f_txt.render(str(valor), True, color)
            pantalla.blit(texto_valor, (x + 120, y - 2))
            y += 32

        y += 10
        pygame.draw.line(pantalla, C['grid_light'], (x, y), (x + 200, y), 1)
        y += 20

        pantalla.blit(f_txt.render("SIGUIENTE", True, C['text']), (x, y))
        self._mini_pieza(self.siguiente, x + 40, y + 25)
        y += 110

        pygame.draw.line(pantalla, C['grid_light'], (x, y), (x + 200, y), 1)
        y += 20

        pantalla.blit(f_pequena.render("CONTROLES:", True, C['cyan']), (x, y))
        y += 25
        controles = [
            ("← →", "Mover"),
            ("↑", "Rotar"),
            ("↓", "Caída suave"),
            ("ESPACIO", "Caída dura"),
            ("P", "Pausa")
        ]
        for tecla, accion in controles:
            pantalla.blit(f_pequena.render(f"{tecla:10} {accion}", True, (160, 160, 180)), (x, y))
            y += 22

    def _mini_pieza(self, p, x, y):
        for r, fila in enumerate(p.forma):
            for c, val in enumerate(fila):
                if val:
                    dibujar_bloque_3d(pantalla, x + c*20, y + r*20, p.color, p.color_light, p.color_dark, 20)

    def _overlay(self, titulo, sub, boton):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        pantalla.blit(s, (0, 0))

        color_titulo = C['gold'] if "VICTORIA" in titulo else C['red']
        titulo_surf = f_titulo.render(titulo, True, color_titulo)
        titulo_rect = titulo_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 80))
        pantalla.blit(titulo_surf, titulo_rect.topleft)

        sub_surf = f_txt.render(sub, True, C['text'])
        sub_rect = sub_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
        pantalla.blit(sub_surf, sub_rect.topleft)

        if boton:
            btn_reiniciar.dibujar(pantalla)
            btn_menu.dibujar(pantalla)

btn_jugar = Boton(WIDTH//2 - 100, 300, 200, 50, "JUGAR", C['green'])
btn_salir = Boton(WIDTH//2 - 100, 370, 200, 50, "SALIR", C['red'])
btn_reiniciar = Boton(WIDTH//2 - 110, HEIGHT//2 + 40, 220, 45, "REINICIAR", C['cyan'])
btn_menu = Boton(WIDTH//2 - 110, HEIGHT//2 + 100, 220, 45, "MENÚ PRINCIPAL", C['purple'])

def main():
    juego = TetrisGame()

    while True:
        dt = reloj.tick(FPS)
        eventos = pygame.event.get()

        for e in eventos:
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if juego.estado == "menu":
                if btn_jugar.actualizar(eventos):
                    juego.reset()
                    juego.estado = "jugando"
                if btn_salir.actualizar(eventos):
                    pygame.quit()
                    sys.exit()

            elif juego.estado == "jugando":
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_LEFT:
                        juego.mover(-1, 0)
                    if e.key == pygame.K_RIGHT:
                        juego.mover(1, 0)
                    if e.key == pygame.K_DOWN:
                        juego.mover(0, 1)
                    if e.key == pygame.K_UP:
                        juego.rotar_pieza()
                    if e.key == pygame.K_SPACE:
                        juego.hard_drop()
                    if e.key == pygame.K_p:
                        juego.estado = "pausado"

            elif juego.estado == "pausado":
                if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
                    juego.estado = "jugando"

            elif juego.estado in ("gameover", "victoria"):
                if btn_reiniciar.actualizar(eventos):
                    juego.reset()
                    juego.estado = "jugando"
                if btn_menu.actualizar(eventos):
                    juego.reset()

        juego.actualizar(dt)
        juego.dibujar()

if __name__ == "__main__":
    main()
