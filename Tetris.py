import pygame
import random
import sys
import math

pygame.init()
pygame.mixer.init()

CELL = 30
COLS, ROWS = 10, 20
PANEL_W = 250
WIDTH = COLS * CELL + PANEL_W
HEIGHT = ROWS * CELL
FPS = 60
LINEAS_OBJETIVO = 30

C = {
    'bg': (8, 8, 15), 'grid': (25, 25, 40), 'grid_light': (35, 35, 55),
    'I': (0, 255, 255), 'O': (255, 255, 0), 'T': (180, 0, 255),
    'S': (0, 255, 100), 'Z': (255, 0, 85), 'J': (0, 100, 255), 'L': (255, 180, 0),
    'ghost': (80, 80, 120), 'panel': (15, 15, 28), 'text': (240, 240, 255),
    'gold': (255, 215, 0), 'cyan': (0, 255, 255), 'purple': (180, 0, 255),
    'green': (0, 255, 100), 'red': (255, 0, 85), 'white': (255, 255, 255),
    'orange': (255, 140, 0), 'pink': (255, 20, 147)
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
pygame.display.set_caption("⚡ TETRIS NEON - ULTRA GAMER EDITION")
reloj = pygame.time.Clock()

try:
    f_titulo = pygame.font.SysFont("consolas", 36, bold=True)
    f_txt = pygame.font.SysFont("consolas", 20, bold=True)
    f_btn = pygame.font.SysFont("consolas", 22, bold=True)
    f_pequena = pygame.font.SysFont("consolas", 16)
    f_epica = pygame.font.SysFont("impact", 48, bold=True)  # Fuente épica
except:
    f_titulo = pygame.font.Font(None, 36)
    f_txt = pygame.font.Font(None, 20)
    f_btn = pygame.font.Font(None, 22)
    f_pequena = pygame.font.Font(None, 16)
    f_epica = pygame.font.Font(None, 48)

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

class Estela:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.life = 15
        self.max_life = 15

    def actualizar(self):
        self.life -= 1

    def dibujar(self, superficie):
        if self.life > 0:
            alpha = int(150 * (self.life / self.max_life))
            rect = pygame.Rect(self.x, self.y, CELL, CELL)
            s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
            pygame.draw.rect(s, (*self.color, alpha), s.get_rect(), border_radius=4)
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
    """Texto flotante ÉPICO con efectos de escala y glow"""
    def __init__(self, texto, x, y, color, size=48, epico=False):
        self.texto = texto
        self.x = x
        self.y = y
        self.color = color
        self.life = 90 if epico else 60
        self.max_life = self.life
        self.size = size
        self.epico = epico
        self.scale = 2.0 if epico else 1.5  # Empieza grande
        self.rotation = 0

    def actualizar(self):
        self.life -= 1
        self.y -= 1.5 if self.epico else 1
        # Escala que se reduce con el tiempo
        self.scale = max(1.0, self.scale - 0.05)
        if self.epico:
            self.rotation = math.sin(self.life * 0.2) * 3

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

class FlashPantalla:
    """Flash de pantalla al hacer algo épico"""
    def __init__(self):
        self.color = (255, 255, 255)
        self.alpha = 0
        self.duracion = 0

    def activar(self, color=(255, 255, 255), duracion=15):
        self.color = color
        self.alpha = 200
        self.duracion = duracion

    def actualizar(self):
        if self.duracion > 0:
            self.duracion -= 1
            self.alpha = int(200 * (self.duracion / 15))
            return True
        return False

    def dibujar(self, superficie):
        if self.duracion > 0:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((*self.color, self.alpha))
            superficie.blit(s, (0, 0))

class ParticulaFondo:
    def __init__(self):
        self.reset()
        self.y = random.randint(0, HEIGHT)

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT + 10
        self.size = random.uniform(1, 4)
        self.speed = random.uniform(0.3, 1.5)
        self.color = random.choice([C['cyan'], C['purple'], C['green'], C['gold']])
        self.alpha = random.randint(60, 180)

    def actualizar(self):
        self.y -= self.speed
        self.x += math.sin(self.y * 0.01) * 0.3
        if self.y < -10:
            self.reset()

    def dibujar(self, superficie):
        s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        s.fill((*self.color, self.alpha))
        superficie.blit(s, (int(self.x - self.size), int(self.y - self.size)))

particulas_fondo = [ParticulaFondo() for _ in range(60)]

def dibujar_fondo_gamer(tick):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        color = (int(5 + ratio * 10), int(3 + ratio * 5), int(10 + ratio * 15))
        pygame.draw.line(pantalla, color, (0, y), (WIDTH, y))

    horizonte_y = HEIGHT // 2 + 50

    for i in range(15):
        t = i / 15
        y = int(horizonte_y + (HEIGHT - horizonte_y) * (t ** 1.6))
        alpha = int(30 + t * 50)
        s = pygame.Surface((WIDTH, 1), pygame.SRCALPHA)
        s.fill((C['purple'][0]//3, C['purple'][1]//4, C['purple'][2]//2, alpha))
        pantalla.blit(s, (0, y))

    centro_x = WIDTH // 2
    for i in range(-12, 13):
        offset = i * 50
        x_top = centro_x + offset // 10
        x_bottom = centro_x + offset * 3
        pygame.draw.line(pantalla, (C['purple'][0]//4, C['purple'][1]//5, C['purple'][2]//3, 80),
                        (x_top, horizonte_y), (x_bottom, HEIGHT), 1)

    s_hor = pygame.Surface((WIDTH, 2), pygame.SRCALPHA)
    pulse = (math.sin(tick * 0.05) + 1) / 2
    s_hor.fill((C['cyan'][0], C['cyan'][1], C['cyan'][2], int(80 + pulse * 100)))
    pantalla.blit(s_hor, (0, horizonte_y))

    for p in particulas_fondo:
        p.actualizar()
        p.dibujar(pantalla)

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
        s.fill((*color, 40))
        superficie.blit(s, glow_rect_scaled.topleft)

    superficie.blit(texto_glow, glow_rect.topleft)

class Boton:
    def __init__(self, x, y, ancho, alto, texto, color_base):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_base = color_base
        self.color_hover = tuple(min(255, int(c * 1.3)) for c in color_base)
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
        factor = 0.15 if self.hover else 0.08
        self.color_actual = [
            max(0, min(255, int(self.color_actual[i] + (target_color[i] - self.color_actual[i]) * factor)))
            for i in range(3)
        ]

        glow_size = 6 + int(pulse * 6)
        glow_rect = self.rect.inflate(glow_size * 2, glow_size * 2)
        glow_alpha = int(40 + pulse * 40)
        glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*self.color_actual, glow_alpha),
                         glow_surface.get_rect(), border_radius=12)
        superficie.blit(glow_surface, glow_rect.topleft)

        border_rect = self.rect.inflate(2, 2)
        pygame.draw.rect(superficie, (*self.color_actual, 200), border_rect, 2, border_radius=10)

        base_color = tuple(max(0, c - 80) for c in self.color_actual)
        pygame.draw.rect(superficie, base_color, self.rect, border_radius=10)

        for i in range(self.rect.height):
            ratio = i / self.rect.height
            alpha = int(140 * (1 - ratio * 0.6))
            grad_rect = pygame.Rect(self.rect.x, self.rect.y + i, self.rect.width, 1)
            s = pygame.Surface((self.rect.width, 1), pygame.SRCALPHA)
            s.fill((*self.color_actual, alpha))
            superficie.blit(s, grad_rect.topleft)

        inner_rect = self.rect.inflate(-2, -2)
        pygame.draw.rect(superficie, (255, 255, 255, 100), inner_rect, 1, border_radius=9)

        texto_sombra = f_btn.render(self.texto, True, (0, 0, 0))
        texto_sombra_rect = texto_sombra.get_rect(center=self.rect.center)
        texto_sombra_rect.y += 2
        superficie.blit(texto_sombra, texto_sombra_rect.topleft)

        texto_surf = f_btn.render(self.texto, True, (240, 240, 240))
        texto_rect = texto_surf.get_rect(center=self.rect.center)

        for offset in range(2, 0, -1):
            glow_text = pygame.transform.scale(texto_surf,
                (texto_surf.get_width() + offset*2, texto_surf.get_height() + offset*2))
            glow_rect_t = glow_text.get_rect(center=texto_rect.center)
            s = pygame.Surface(glow_text.get_size(), pygame.SRCALPHA)
            s.fill((*self.color_actual, 80))
            superficie.blit(s, glow_rect_t.topleft)

        superficie.blit(texto_surf, texto_rect.topleft)

class Pieza:
    def __init__(self, tipo, x=None, y=None):
        self.tipo = tipo
        self.forma = [fila[:] for fila in SHAPES[tipo]]
        self.x = x if x is not None else COLS//2 - len(self.forma[0])//2
        self.y = y if y is not None else 0
        self.color = C[tipo]

    def rotar(self):
        return [list(fila) for fila in zip(*self.forma[::-1])]

    def clonar(self):
        return Pieza(self.tipo, self.x, self.y)

class TetrisGame:
    def __init__(self):
        self.reset()
        self.particulas = []
        self.estelas = []
        self.textos_flotantes = []
        self.shake = ScreenShake()
        self.flash = FlashPantalla()
        self.tick_anim = 0
        self.combo = 0
        self.ultimo_hard_drop = False
        self.tetris_count = 0  

    def reset(self):
        self.grid = [[None]*COLS for _ in range(ROWS)]
        self.piezas = list(SHAPES.keys())
        self.bolsa = []
        self.actual = self._next_piece()
        self.siguiente = self._next_piece()
        self.puntaje, self.lineas, self.nivel = 0, 0, 1
        self.estado = "menu"
        self.drop_timer = 0
        self.drop_delay = 800
        self.confeti = []
        self.particulas = []
        self.estelas = []
        self.textos_flotantes = []
        self.combo = 0
        self.ultimo_hard_drop = False
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
        for r, fila in enumerate(self.actual.forma):
            for c, val in enumerate(fila):
                if val:
                    if self.actual.y + r < 0:
                        self.estado = "gameover"
                        return
                    self.grid[self.actual.y + r][self.actual.x + c] = self.actual.color
        self._crear_particulas_fijacion()
        self._limpiar_lineas()
        self.actual = self.siguiente
        self.siguiente = self._next_piece()
        if self._colision(self.actual):
            self.estado = "gameover"

    def _crear_particulas_fijacion(self):
        intensidad = 8 if self.ultimo_hard_drop else 5
        for r, fila in enumerate(self.actual.forma):
            for c, val in enumerate(fila):
                if val:
                    x = (self.actual.x + c) * CELL + CELL//2
                    y = (self.actual.y + r) * CELL + CELL//2
                    for _ in range(intensidad):
                        vx = random.uniform(-4, 4)
                        vy = random.uniform(-4, 2)
                        self.particulas.append(Particula(x, y, self.actual.color, vx, vy, random.randint(2, 5), 35))

    def _limpiar_lineas(self):
        lineas_limpias = 0
        for i in range(ROWS-1, -1, -1):
            if all(self.grid[i]):
                for c in range(COLS):
                    x = c * CELL + CELL//2
                    y = i * CELL + CELL//2
                    for _ in range(10):
                        vx = random.uniform(-5, 5)
                        vy = random.uniform(-6, -1)
                        self.particulas.append(Particula(x, y, C['gold'], vx, vy, random.randint(3, 7), 45))

                self.grid.pop(i)
                self.grid.insert(0, [None]*COLS)
                lineas_limpias += 1

        if lineas_limpias > 0:
            self.combo += 1
            pts = {1:100, 2:300, 3:500, 4:800}
            bonus_combo = self.combo * 50
            puntos_ganados = (pts.get(lineas_limpias, 0) + bonus_combo) * self.nivel
            self.puntaje += puntos_ganados
            self.lineas += lineas_limpias
            self.nivel = self.lineas // 10 + 1
            self.drop_delay = max(50, 800 - (self.nivel-1)*60)

            self._mostrar_mensaje_epico(lineas_limpias)

            self.shake.activar(intensidad=lineas_limpias * 3, duracion=15)

            if self.lineas >= LINEAS_OBJETIVO:
                self.estado = "victoria"
                self._generar_confeti()
        else:
            self.combo = 0

    def _mostrar_mensaje_epico(self, lineas):
        """Muestra mensajes GAMER épicos según las líneas limpiadas"""
        centro_x = COLS * CELL // 2
        centro_y = HEIGHT // 2

        if lineas == 1:
            mensajes = ["NICE!", "CLEAN!", "SOLID!", "GOOD!"]
            msg = random.choice(mensajes)
            self.textos_flotantes.append(TextoFlotante(
                msg, centro_x, centro_y, C['white'], 40, epico=False
            ))

        elif lineas == 2:
            mensajes = ["DOUBLE BLAST!", "TWIN STRIKE!", "DOUBLE KILL!"]
            msg = random.choice(mensajes)
            self.textos_flotantes.append(TextoFlotante(
                msg, centro_x, centro_y, C['cyan'], 48, epico=True
            ))
            self.flash.activar(C['cyan'], 10)

        elif lineas == 3:
            mensajes = ["TRIPLE STRIKE!", "TRIPLE KILL!", "TRIPLE BLAST!"]
            msg = random.choice(mensajes)
            self.textos_flotantes.append(TextoFlotante(
                msg, centro_x, centro_y, C['green'], 52, epico=True
            ))
            self.flash.activar(C['green'], 15)

        elif lineas == 4:
            self.tetris_count += 1
            mensajes = ["TETRIS!", "ULTRA TETRIS!", "LEGENDARY!", "GODLIKE!"]
            msg = random.choice(mensajes)
            self.textos_flotantes.append(TextoFlotante(
                msg, centro_x, centro_y, C['gold'], 64, epico=True
            ))
            self.flash.activar(C['gold'], 20)

            for _ in range(50):
                x = random.randint(0, COLS * CELL)
                y = random.randint(0, HEIGHT)
                vx = random.uniform(-8, 8)
                vy = random.uniform(-8, 8)
                self.particulas.append(Particula(x, y, C['gold'], vx, vy, random.randint(4, 8), 60))

        if self.combo >= 2:
            combo_y = centro_y + 80
            if self.combo == 2:
                combo_msg = "COMBO x2! ON FIRE! 🔥"
                combo_color = C['orange']
            elif self.combo == 3:
                combo_msg = "COMBO x3! RAMPAGE! 💥"
                combo_color = C['red']
            elif self.combo == 4:
                combo_msg = "COMBO x4! UNSTOPPABLE! ⚡"
                combo_color = C['purple']
            elif self.combo >= 5:
                combo_msg = f"COMBO x{self.combo}! GODLIKE! 👑"
                combo_color = C['gold']

            self.textos_flotantes.append(TextoFlotante(
                combo_msg, centro_x, combo_y, combo_color, 36, epico=True
            ))

    def _generar_confeti(self):
        self.confeti = []
        colores = [C['cyan'], C['green'], C['purple'], C['gold'], C['red']]
        for _ in range(200):
            self.confeti.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(-HEIGHT, 0),
                'r': random.randint(3, 7),
                'c': random.choice(colores),
                'vy': random.uniform(3, 7),
                'vx': random.uniform(-3, 3)
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
                self.drop_timer = 0

    def rotar_pieza(self):
        if self.estado != "jugando":
            return
        original = [fila[:] for fila in self.actual.forma]
        self.actual.forma = self.actual.rotar()
        for dx in [0, -1, 1, -2, 2]:
            if not self._colision(self.actual, dx):
                self.actual.x += dx
                return
        self.actual.forma = original

    def hard_drop(self):
        if self.estado != "jugando":
            return

        self.ultimo_hard_drop = True
        distancia_caida = 0

        while not self._colision(self.actual, dy=1):
            self.actual.y += 1
            distancia_caida += 1
            self.drop_timer = 0

            for r, fila in enumerate(self.actual.forma):
                for c, val in enumerate(fila):
                    if val:
                        x = (self.actual.x + c) * CELL
                        y = (self.actual.y + r) * CELL
                        self.estelas.append(Estela(x, y, self.actual.color))

        self.shake.activar(intensidad=min(8, distancia_caida // 2), duracion=12)

        for r, fila in enumerate(self.actual.forma):
            for c, val in enumerate(fila):
                if val:
                    x = (self.actual.x + c) * CELL + CELL//2
                    y = (self.actual.y + r) * CELL + CELL//2
                    for _ in range(15):
                        vx = random.uniform(-6, 6)
                        vy = random.uniform(-8, -2)
                        self.particulas.append(Particula(x, y, C['white'], vx, vy, random.randint(3, 6), 40))
                    for _ in range(10):
                        vx = random.uniform(-4, 4)
                        vy = random.uniform(-5, 0)
                        self.particulas.append(Particula(x, y, self.actual.color, vx, vy, random.randint(2, 5), 35))

        self.puntaje += distancia_caida * 2

        self._fijar_pieza()

    def actualizar(self, dt):
        self.tick_anim += 1

        for p in self.particulas[:]:
            p.actualizar()
            if p.life <= 0:
                self.particulas.remove(p)

        for e in self.estelas[:]:
            e.actualizar()
            if e.life <= 0:
                self.estelas.remove(e)

        for t in self.textos_flotantes[:]:
            t.actualizar()
            if t.life <= 0:
                self.textos_flotantes.remove(t)

        self.shake.actualizar()
        self.flash.actualizar()

        if self.estado == "jugando":
            self.drop_timer += dt
            if self.drop_timer >= self.drop_delay:
                self.drop_timer = 0
                if not self._colision(self.actual, dy=1):
                    self.actual.y += 1
                    self.ultimo_hard_drop = False
                else:
                    self._fijar_pieza()

        if self.estado == "victoria":
            for c in self.confeti:
                c['x'] += c['vx']
                c['y'] += c['vy']
                c['vx'] *= 0.99
                if c['y'] > HEIGHT:
                    c['y'] = -10
                    c['x'] = random.randint(0, WIDTH)

    def dibujar(self):
        shake_x, shake_y = self.shake.actualizar()
        pantalla.fill(C['bg'])

        dibujar_fondo_gamer(self.tick_anim)

        game_area = pygame.Surface((COLS*CELL, HEIGHT), pygame.SRCALPHA)
        game_area.fill((10, 10, 20, 180))
        pantalla.blit(game_area, (0, 0))

        for r in range(ROWS):
            for c in range(COLS):
                rect = (c*CELL, r*CELL, CELL, CELL)
                pygame.draw.rect(pantalla, C['grid'], rect, 1)
                if self.grid[r][c]:
                    pygame.draw.rect(pantalla, self.grid[r][c], rect, border_radius=4)
                    pygame.draw.rect(pantalla, (255,255,255,60), rect, 2, border_radius=4)

        for e in self.estelas:
            e.dibujar(pantalla)

        if self.estado == "jugando":
            g = self._ghost()
            for r, fila in enumerate(g.forma):
                for c, val in enumerate(fila):
                    if val:
                        rect_ghost = ((g.x + c) * CELL, (g.y + r) * CELL, CELL, CELL)
                        pygame.draw.rect(pantalla, C['ghost'], rect_ghost, 2, border_radius=3)

        if self.estado in ("jugando", "pausado", "gameover", "victoria"):
            for r, fila in enumerate(self.actual.forma):
                for c, val in enumerate(fila):
                    if val:
                        rect_actual = ((self.actual.x + c) * CELL, (self.actual.y + r) * CELL, CELL, CELL)
                        pygame.draw.rect(pantalla, self.actual.color, rect_actual, border_radius=4)
                        pygame.draw.rect(pantalla, (255,255,255,80), rect_actual, 2, border_radius=4)

        for p in self.particulas:
            p.dibujar(pantalla)

        for t in self.textos_flotantes:
            t.dibujar(pantalla)

        # Flash de pantalla
        if self.flash.dibujar(pantalla):
            self.flash.dibujar(pantalla)

        panel_surf = pygame.Surface((PANEL_W, HEIGHT), pygame.SRCALPHA)
        panel_surf.fill((15, 15, 28, 220))
        pantalla.blit(panel_surf, (COLS*CELL, 0))

        pygame.draw.line(pantalla, C['cyan'], (COLS*CELL, 0), (COLS*CELL, HEIGHT), 2)

        self._dibujar_panel()

        if self.estado == "menu":
            self._dibujar_menu()
        elif self.estado == "pausado":
            self._overlay("PAUSA", "Presiona P para continuar", False)
        elif self.estado == "gameover":
            self._overlay("GAME OVER", f"Líneas: {self.lineas} | Puntos: {self.puntaje:,}", True)
        elif self.estado == "victoria":
            for c in self.confeti:
                pygame.draw.circle(pantalla, c['c'], (int(c['x']), int(c['y'])), c['r'])
            self._overlay("¡LO LOGRASTE!", f"Objetivo: {LINEAS_OBJETIVO} líneas", True)

        for y in range(0, HEIGHT, 4):
            pygame.draw.line(pantalla, (0, 0, 0, 25), (0, y), (WIDTH, y))

        pygame.display.flip()

    def _dibujar_menu(self):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 140))
        pantalla.blit(s, (0, 0))

        dibujar_texto_resplandor("TETRIS NEON", f_titulo, C['cyan'], pantalla, WIDTH//2, 180)
        dibujar_texto_resplandor("ULTRA GAMER EDITION", f_pequena, C['purple'], pantalla, WIDTH//2, 230)

        btn_jugar.dibujar(pantalla)
        btn_salir.dibujar(pantalla)

    def _dibujar_panel(self):
        x = COLS*CELL + 20
        y = 30

        dibujar_texto_resplandor("ESTADÍSTICAS", f_txt, C['gold'], pantalla, x + 100, y, "center")
        y += 40

        stats = [("NIVEL", self.nivel, C['cyan']),
                 ("LÍNEAS", self.lineas, C['green']),
                 ("PUNTOS", f"{self.puntaje:,}", C['gold']),
                 ("COMBO", f"x{self.combo}", C['red'] if self.combo > 0 else C['text']),
                 ("TETRIS", f"{self.tetris_count}", C['purple'])]

        for titulo, valor, color in stats:
            pantalla.blit(f_pequena.render(titulo, True, (150, 150, 170)), (x, y))
            dibujar_texto_resplandor(str(valor), f_txt, color, pantalla, x + 110, y + 2, "left")
            y += 35

        y += 20
        pygame.draw.line(pantalla, C['grid_light'], (x, y), (x + 200, y), 2)
        y += 25

        pantalla.blit(f_txt.render("SIGUIENTE", True, C['text']), (x, y))
        self._mini_pieza(self.siguiente, x + 10, y + 30)

        y += 120
        pygame.draw.line(pantalla, C['grid_light'], (x, y), (x + 200, y), 2)
        y += 25

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
            pantalla.blit(f_pequena.render(f"{tecla:12} {accion}", True, (160, 160, 180)), (x, y))
            y += 22

    def _mini_pieza(self, p, x, y):
        for r, fila in enumerate(p.forma):
            for c, val in enumerate(fila):
                if val:
                    rect = (x + c*18, y + r*18, 16, 16)
                    pygame.draw.rect(pantalla, p.color, rect, border_radius=3)
                    pygame.draw.rect(pantalla, (255, 255, 255, 80), rect, 1, border_radius=3)

    def _overlay(self, titulo, sub, boton):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        pantalla.blit(s, (0, 0))

        color_titulo = C['gold'] if "LOGRASTE" in titulo else C['red']
        dibujar_texto_resplandor(titulo, f_titulo, color_titulo, pantalla, WIDTH//2, HEIGHT//2 - 50)
        dibujar_texto_resplandor(sub, f_txt, C['text'], pantalla, WIDTH//2, HEIGHT//2 + 10)

        if boton:
            btn_reiniciar.dibujar(pantalla)
            btn_menu.dibujar(pantalla)

btn_jugar = Boton(WIDTH//2 - 100, 300, 200, 50, "JUGAR", C['green'])
btn_salir = Boton(WIDTH//2 - 100, 370, 200, 50, "SALIR", C['red'])
btn_reiniciar = Boton(WIDTH//2 - 110, HEIGHT//2 + 70, 220, 45, "REINICIAR", C['cyan'])
btn_menu = Boton(WIDTH//2 - 110, HEIGHT//2 + 130, 220, 45, "MENÚ PRINCIPAL", C['purple'])

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
