import pygame
import sys
import math
import random

pygame.init()
pygame.mixer.init()

ANCHO, ALTO = 900, 700
FPS = 60
PUNTOS_PARA_GANAR = 7

C = {
    'bg': (8, 8, 15),
    'cyan': (0, 255, 255),
    'purple': (180, 0, 255),
    'pink': (255, 0, 128),
    'green': (0, 255, 100),
    'yellow': (255, 230, 0),
    'red': (255, 0, 85),
    'white': (255, 255, 255),
    'grid': (25, 25, 40)
}

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("⚡ PONG NEON - ULTRA GAMER EDITION")
reloj = pygame.time.Clock()

try:
    f_titulo = pygame.font.SysFont("consolas", 48, bold=True)
    f_txt = pygame.font.SysFont("consolas", 28, bold=True)
    f_btn = pygame.font.SysFont("consolas", 24, bold=True)
    f_pequena = pygame.font.SysFont("consolas", 18)
except:
    f_titulo = pygame.font.Font(None, 48)
    f_txt = pygame.font.Font(None, 28)
    f_btn = pygame.font.Font(None, 24)
    f_pequena = pygame.font.Font(None, 18)

def cargar_sonido(nombre):
    try:
        return pygame.mixer.Sound(nombre)
    except:
        return None

sonido_paddle = cargar_sonido("paddle.wav")
sonido_punto = cargar_sonido("punto.wav")
sonido_pared = cargar_sonido("pared.wav")

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
        self.size *= 0.97

    def dibujar(self, superficie):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            superficie.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class Trail:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.life = 10
        self.size = 8

    def actualizar(self):
        self.life -= 1
        self.size *= 0.9

    def dibujar(self, superficie):
        if self.life > 0:
            alpha = int(150 * (self.life / 10))
            s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            superficie.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class ParticulaFondo:
    def __init__(self):
        self.reset()
        self.y = random.randint(0, ALTO)

    def reset(self):
        self.x = random.randint(0, ANCHO)
        self.y = ALTO + 10
        self.size = random.uniform(1, 4)
        self.speed = random.uniform(0.5, 2)
        self.color = random.choice([C['cyan'], C['purple'], C['pink'], C['green']])
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

particulas_fondo = [ParticulaFondo() for _ in range(80)]

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

def dibujar_fondo_gamer(tick):
    for y in range(ALTO):
        ratio = y / ALTO
        color = (int(5 + ratio * 8), int(3 + ratio * 4), int(10 + ratio * 12))
        pygame.draw.line(pantalla, color, (0, y), (ANCHO, y))

    horizonte_y = ALTO // 2 + 60

    for i in range(15):
        t = i / 15
        y = int(horizonte_y + (ALTO - horizonte_y) * (t ** 1.6))
        alpha = int(25 + t * 45)
        s = pygame.Surface((ANCHO, 1), pygame.SRCALPHA)
        s.fill((C['purple'][0]//3, C['purple'][1]//4, C['purple'][2]//2, alpha))
        pantalla.blit(s, (0, y))

    centro_x = ANCHO // 2
    for i in range(-15, 16):
        offset = i * 40
        x_top = centro_x + offset // 12
        x_bottom = centro_x + offset * 3
        pygame.draw.line(pantalla, (C['purple'][0]//4, C['purple'][1]//5, C['purple'][2]//3),
                        (x_top, horizonte_y), (x_bottom, ALTO), 1)

    s_hor = pygame.Surface((ANCHO, 2), pygame.SRCALPHA)
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

class PongGame:
    def __init__(self):
        self.reset()
        self.particulas = []
        self.trails = []
        self.tick_anim = 0

    def reset(self):
        self.paddle_ancho = 15
        self.paddle_alto = 90
        self.paddle_vel = 7

        self.player_y = ALTO // 2 - self.paddle_alto // 2
        self.cpu_y = ALTO // 2 - self.paddle_alto // 2

        self.ball_size = 10
        self.ball_x = ANCHO // 2
        self.ball_y = ALTO // 2
        self.ball_vel_x = 5 * random.choice([1, -1])
        self.ball_vel_y = 3 * random.choice([1, -1])

        self.player_score = 0
        self.cpu_score = 0
        self.estado = "menu"
        self.pausa_timer = 0
        self.ganador = None

    def crear_particulas(self, x, y, color, cantidad=15):
        for _ in range(cantidad):
            vx = random.uniform(-4, 4)
            vy = random.uniform(-4, 4)
            size = random.randint(2, 5)
            life = random.randint(20, 35)
            self.particulas.append(Particula(x, y, color, vx, vy, size, life))

    def reset_ball(self):
        self.ball_x = ANCHO // 2
        self.ball_y = ALTO // 2
        self.ball_vel_x = 5 * random.choice([1, -1])
        self.ball_vel_y = 3 * random.choice([1, -1])
        self.pausa_timer = 60

    def actualizar(self):
        self.tick_anim += 1

        for p in self.particulas[:]:
            p.actualizar()
            if p.life <= 0:
                self.particulas.remove(p)

        for t in self.trails[:]:
            t.actualizar()
            if t.life <= 0:
                self.trails.remove(t)

        if self.estado == "jugando":
            if self.pausa_timer > 0:
                self.pausa_timer -= 1
                return

            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_UP] or teclas[pygame.K_w]:
                self.player_y -= self.paddle_vel
            if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
                self.player_y += self.paddle_vel

            self.player_y = max(0, min(ALTO - self.paddle_alto, self.player_y))

            cpu_center = self.cpu_y + self.paddle_alto // 2
            if cpu_center < self.ball_y - 10:
                self.cpu_y += self.paddle_vel * 0.85
            elif cpu_center > self.ball_y + 10:
                self.cpu_y -= self.paddle_vel * 0.85

            self.cpu_y = max(0, min(ALTO - self.paddle_alto, self.cpu_y))

            if self.tick_anim % 2 == 0:
                self.trails.append(Trail(self.ball_x, self.ball_y, C['cyan']))

            self.ball_x += self.ball_vel_x
            self.ball_y += self.ball_vel_y

            if self.ball_y <= 0 or self.ball_y >= ALTO - self.ball_size:
                self.ball_vel_y *= -1
                self.crear_particulas(self.ball_x, self.ball_y, C['yellow'], 8)
                if sonido_pared: sonido_pared.play()

            if (self.ball_x <= 50 + self.paddle_ancho and
                self.ball_x >= 50 and
                self.ball_y + self.ball_size >= self.player_y and
                self.ball_y <= self.player_y + self.paddle_alto):

                self.ball_vel_x = abs(self.ball_vel_x) * 1.05
                self.ball_vel_x = min(self.ball_vel_x, 15)

                relative_intersect = (self.player_y + self.paddle_alto/2) - self.ball_y
                normalized = relative_intersect / (self.paddle_alto/2)
                self.ball_vel_y = -normalized * 6

                self.crear_particulas(self.ball_x, self.ball_y, C['cyan'], 20)
                if sonido_paddle: sonido_paddle.play()

            if (self.ball_x + self.ball_size >= ANCHO - 50 - self.paddle_ancho and
                self.ball_x + self.ball_size <= ANCHO - 50 and
                self.ball_y + self.ball_size >= self.cpu_y and
                self.ball_y <= self.cpu_y + self.paddle_alto):

                self.ball_vel_x = -abs(self.ball_vel_x) * 1.05
                self.ball_vel_x = max(self.ball_vel_x, -15)

                relative_intersect = (self.cpu_y + self.paddle_alto/2) - self.ball_y
                normalized = relative_intersect / (self.paddle_alto/2)
                self.ball_vel_y = -normalized * 6

                self.crear_particulas(self.ball_x, self.ball_y, C['pink'], 20)
                if sonido_paddle: sonido_paddle.play()

            if self.ball_x < 0:
                self.cpu_score += 1
                self.crear_particulas(0, self.ball_y, C['red'], 30)
                if sonido_punto: sonido_punto.play()
                self.reset_ball()
            elif self.ball_x > ANCHO:
                self.player_score += 1
                self.crear_particulas(ANCHO, self.ball_y, C['green'], 30)
                if sonido_punto: sonido_punto.play()
                self.reset_ball()

            if self.player_score >= PUNTOS_PARA_GANAR:
                self.estado = "gameover"
                self.ganador = "player"
            elif self.cpu_score >= PUNTOS_PARA_GANAR:
                self.estado = "gameover"
                self.ganador = "cpu"

    def dibujar(self):
        dibujar_fondo_gamer(self.tick_anim)

        game_area = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        game_area.fill((10, 10, 20, 150))
        pantalla.blit(game_area, (0, 0))

        for y in range(0, ALTO, 20):
            color = C['cyan'] if (y // 20) % 2 == 0 else C['purple']
            pygame.draw.rect(pantalla, color, (ANCHO//2 - 2, y, 4, 10), border_radius=2)

        dibujar_texto_resplandor(str(self.player_score), f_titulo, C['cyan'], pantalla, ANCHO//2 - 80, 40)
        dibujar_texto_resplandor(str(self.cpu_score), f_titulo, C['pink'], pantalla, ANCHO//2 + 80, 40)
        pantalla.blit(f_pequena.render("PLAYER", True, C['cyan']), (ANCHO//2 - 80, 85))
        pantalla.blit(f_pequena.render("CPU", True, C['pink']), (ANCHO//2 + 95, 85))

        for t in self.trails:
            t.dibujar(pantalla)

        for p in self.particulas:
            p.dibujar(pantalla)

        glow_rect_p = pygame.Rect(50 - 4, self.player_y - 4, self.paddle_ancho + 8, self.paddle_alto + 8)
        s = pygame.Surface(glow_rect_p.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (*C['cyan'], 80), s.get_rect(), border_radius=8)
        pantalla.blit(s, (50 - 4, self.player_y - 4))
        pygame.draw.rect(pantalla, C['cyan'], (50, self.player_y, self.paddle_ancho, self.paddle_alto), border_radius=6)
        pygame.draw.rect(pantalla, (255,255,255,100), (50, self.player_y, self.paddle_ancho, self.paddle_alto), 2, border_radius=6)

        glow_rect_c = pygame.Rect(ANCHO - 50 - self.paddle_ancho - 4, self.cpu_y - 4, self.paddle_ancho + 8, self.paddle_alto + 8)
        s = pygame.Surface(glow_rect_c.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (*C['pink'], 80), s.get_rect(), border_radius=8)
        pantalla.blit(s, (ANCHO - 50 - self.paddle_ancho - 4, self.cpu_y - 4))
        pygame.draw.rect(pantalla, C['pink'], (ANCHO - 50 - self.paddle_ancho, self.cpu_y, self.paddle_ancho, self.paddle_alto), border_radius=6)
        pygame.draw.rect(pantalla, (255,255,255,100), (ANCHO - 50 - self.paddle_ancho, self.cpu_y, self.paddle_ancho, self.paddle_alto), 2, border_radius=6)

        glow_rect_b = pygame.Rect(self.ball_x - self.ball_size - 4, self.ball_y - self.ball_size - 4,
                                   self.ball_size*2 + 8, self.ball_size*2 + 8)
        s = pygame.Surface(glow_rect_b.size, pygame.SRCALPHA)
        pygame.draw.circle(s, (*C['cyan'], 100), (self.ball_size + 4, self.ball_size + 4), self.ball_size + 4)
        pantalla.blit(s, (self.ball_x - self.ball_size - 4, self.ball_y - self.ball_size - 4))
        pygame.draw.circle(pantalla, C['cyan'], (int(self.ball_x), int(self.ball_y)), self.ball_size)
        pygame.draw.circle(pantalla, C['white'], (int(self.ball_x), int(self.ball_y)), self.ball_size, 2)

        if self.estado == "menu":
            self._dibujar_menu()
        elif self.estado == "pausado":
            self._overlay("PAUSA", "Presiona P para continuar")
        elif self.estado == "gameover":
            self._dibujar_gameover()

        for y in range(0, ALTO, 4):
            pygame.draw.line(pantalla, (0, 0, 0, 25), (0, y), (ANCHO, y))

        pygame.display.flip()

    def _dibujar_menu(self):
        s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        pantalla.blit(s, (0, 0))

        dibujar_texto_resplandor("PONG NEON", f_titulo, C['cyan'], pantalla, ANCHO//2, 180)
        dibujar_texto_resplandor("ULTRA GAMER EDITION", f_pequena, C['purple'], pantalla, ANCHO//2, 240)

        btn_jugar.dibujar(pantalla)
        btn_salir.dibujar(pantalla)

        instrucciones = ["Controles: ↑↓ o W/S para mover", f"Primero en llegar a {PUNTOS_PARA_GANAR} gana"]
        for i, txt in enumerate(instrucciones):
            pantalla.blit(f_pequena.render(txt, True, (150, 150, 170)), (ANCHO//2 - 150, 480 + i*30))

    def _dibujar_gameover(self):
        s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        pantalla.blit(s, (0, 0))

        if self.ganador == "player":
            dibujar_texto_resplandor("¡VICTORIA!", f_titulo, C['green'], pantalla, ANCHO//2, ALTO//2 - 80)
            dibujar_texto_resplandor("¡GANASTE!", f_txt, C['cyan'], pantalla, ANCHO//2, ALTO//2 - 30)
        else:
            dibujar_texto_resplandor("DERROTA", f_titulo, C['red'], pantalla, ANCHO//2, ALTO//2 - 80)
            dibujar_texto_resplandor("LA CPU GANÓ", f_txt, C['pink'], pantalla, ANCHO//2, ALTO//2 - 30)

        dibujar_texto_resplandor(f"{self.player_score} - {self.cpu_score}", f_titulo, C['white'], pantalla, ANCHO//2, ALTO//2 + 20)

        btn_reintentar.dibujar(pantalla)
        btn_menu.dibujar(pantalla)

    def _overlay(self, titulo, sub):
        s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        pantalla.blit(s, (0, 0))
        dibujar_texto_resplandor(titulo, f_titulo, C['yellow'], pantalla, ANCHO//2, ALTO//2 - 30)
        dibujar_texto_resplandor(sub, f_txt, C['white'], pantalla, ANCHO//2, ALTO//2 + 20)

btn_jugar = Boton(ANCHO//2 - 100, 320, 200, 50, "JUGAR", C['green'])
btn_salir = Boton(ANCHO//2 - 100, 390, 200, 50, "SALIR", C['red'])
btn_reintentar = Boton(ANCHO//2 - 110, ALTO//2 + 80, 220, 45, "REINTENTAR", C['cyan'])
btn_menu = Boton(ANCHO//2 - 110, ALTO//2 + 140, 220, 45, "MENÚ PRINCIPAL", C['purple'])

def main():
    juego = PongGame()

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
                    if e.key == pygame.K_p:
                        juego.estado = "pausado"
                    if e.key == pygame.K_ESCAPE:
                        juego.estado = "menu"

            elif juego.estado == "pausado":
                if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
                    juego.estado = "jugando"
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    juego.estado = "menu"

            elif juego.estado == "gameover":
                if btn_reintentar.actualizar(eventos):
                    juego.reset()
                    juego.estado = "jugando"
                if btn_menu.actualizar(eventos):
                    juego.reset()

        juego.actualizar()
        juego.dibujar()

if __name__ == "__main__":
    main()
