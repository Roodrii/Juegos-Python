import pygame
import sys
import random
import math

pygame.init()

ANCHO, ALTO = 700, 800
FPS = 60
TAM_PIXEL = 3

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE = (0, 255, 100)
VERDE_OSCURO = (0, 180, 70)
ROJO = (255, 0, 85)
CYAN = (0, 255, 255)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("SPACE INVADERS - ARCADE CLASSIC")
reloj = pygame.time.Clock()

# Sprites estilo Space Invaders clásico
SPRITE_JUGADOR = [
    [0,0,0,0,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,1,1,1,1,0,0,0,0,0],
    [0,0,0,1,1,1,1,1,1,0,0,0,0],
    [0,1,1,1,1,1,1,1,1,1,1,0,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1],
]

SPRITE_ALIEN1 = [
    [0,0,1,0,0,0,0,0,1,0,0],
    [0,0,0,1,0,0,0,1,0,0,0],
    [0,0,1,1,1,1,1,1,1,0,0],
    [0,1,1,0,1,1,1,0,1,1,0],
    [1,1,1,1,1,1,1,1,1,1,1],
    [1,0,1,1,1,1,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,1,0,1],
    [0,0,0,1,1,0,1,1,0,0,0],
]

SPRITE_ALIEN2 = [
    [0,0,0,1,1,0,0,0],
    [0,0,1,1,1,1,0,0],
    [0,1,1,1,1,1,1,0],
    [1,1,0,1,1,0,1,1],
    [1,1,1,1,1,1,1,1],
    [0,0,1,0,0,1,0,0],
    [0,1,0,1,1,0,1,0],
    [1,0,1,0,0,1,0,1],
]

SPRITE_ALIEN3 = [
    [0,0,1,0,0],
    [0,1,1,1,0],
    [1,1,1,1,1],
    [1,0,1,0,1],
    [0,1,1,1,0],
    [1,0,0,0,1],
    [0,1,0,1,0],
]

SPRITE_UFO = [
    [0,0,0,0,0,1,1,1,1,0,0,0,0,0],
    [0,0,0,1,1,1,1,1,1,1,1,0,0,0],
    [0,0,1,1,1,1,1,1,1,1,1,1,0,0],
    [0,1,0,1,0,1,0,1,0,1,0,1,1,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,0,1,1,1,0,0,0,0,1,1,1,0,0],
    [0,0,0,1,0,0,0,0,0,0,1,0,0,0],
]

SPRITE_BUNKER = [
    [0,0,1,1,1,1,1,1,1,1,1,1,0,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,0,0,0,0,0,0,1,1,1,1],
    [1,1,1,0,0,0,0,0,0,0,0,1,1,1],
    [1,1,0,0,0,0,0,0,0,0,0,0,1,1],
]

try:
    f_titulo = pygame.font.SysFont('consolas', 48, bold=True)
    f_texto = pygame.font.SysFont('consolas', 24, bold=True)
    f_pequena = pygame.font.SysFont('consolas', 18, bold=True)
    f_marcador = pygame.font.SysFont('consolas', 20, bold=True)
except:
    f_titulo = pygame.font.Font(None, 48)
    f_texto = pygame.font.Font(None, 24)
    f_pequena = pygame.font.Font(None, 18)
    f_marcador = pygame.font.Font(None, 20)

def dibujar_sprite(sprite, x, y, color, tam_pixel=TAM_PIXEL):
    for fila_idx, fila in enumerate(sprite):
        for col_idx, pixel in enumerate(fila):
            if pixel != 0:
                rect = pygame.Rect(int(x) + col_idx * tam_pixel, int(y) + fila_idx * tam_pixel, tam_pixel, tam_pixel)
                if rect.right > 0 and rect.left < ANCHO and rect.bottom > 0 and rect.top < ALTO:
                    pygame.draw.rect(pantalla, color, rect)

def dibujar_texto_arcade(texto, fuente, color, x, y, centro=True):
    t = fuente.render(texto, True, color)
    r = t.get_rect()
    if centro:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    pantalla.blit(t, r.topleft)

class Estrella:
    def __init__(self):
        self.x = random.randint(0, ANCHO)
        self.y = random.randint(0, ALTO)
        self.size = random.choice([1, 2])
    def dibujar(self):
        pygame.draw.rect(pantalla, BLANCO, (int(self.x), int(self.y), self.size, self.size))

class Particula:
    def __init__(self, x, y, color):
        self.x, self.y = float(x), float(y)
        self.color = color
        angulo = random.uniform(0, math.pi*2)
        velocidad = random.uniform(1, 5)
        self.vx = math.cos(angulo) * velocidad
        self.vy = math.sin(angulo) * velocidad
        self.life = random.randint(15, 30)
        self.max_life = self.life
        self.size = random.randint(2, 4)
    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
    def dibujar(self):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            surf = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            pantalla.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

class Jugador:
    def __init__(self):
        self.w = 13 * TAM_PIXEL
        self.h = 8 * TAM_PIXEL
        self.x = ANCHO//2 - self.w//2
        self.y = ALTO - 100
        self.speed = 5
        self.vidas = 3
        self.colores = {1: VERDE}
        self.cooldown = 0  # Temporizador para disparo rápido

    def mover(self, teclas):
        if teclas[pygame.K_LEFT] and self.x > 0: self.x -= self.speed
        if teclas[pygame.K_RIGHT] and self.x < ANCHO - self.w: self.x += self.speed

    def disparar(self, balas):
        # Disparo más rápido: cooldown reducido a 15 frames (4 disparos por segundo)
        if self.cooldown <= 0:
            balas.append(Bala(self.x + self.w//2, self.y, -10, True))
            self.cooldown = 15  # Reducido de 30 a 15 para disparo más rápido

    def actualizar(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def dibujar(self):
        dibujar_sprite(SPRITE_JUGADOR, self.x, self.y, VERDE, TAM_PIXEL)

class Alien:
    def __init__(self, x, y, tipo, fila):
        self.x = float(x)
        self.y = float(y)
        self.tipo = tipo
        self.fila = fila
        self.w = 11 * TAM_PIXEL if tipo == 1 else (8 * TAM_PIXEL if tipo == 2 else 5 * TAM_PIXEL)
        self.h = 8 * TAM_PIXEL
        self.frame = 0
        self.frame_timer = 0

        if fila >= 4:
            self.puntos = 10
        elif fila >= 2:
            self.puntos = 20
        else:
            self.puntos = 30

    def actualizar(self, dx, dy):
        self.x += dx
        self.y += dy
        self.frame_timer += 1
        if self.frame_timer > 30:
            self.frame = 1 - self.frame
            self.frame_timer = 0

    def dibujar(self):
        if self.tipo == 1:
            sprite = SPRITE_ALIEN1
        elif self.tipo == 2:
            sprite = SPRITE_ALIEN2
        else:
            sprite = SPRITE_ALIEN3
        dibujar_sprite(sprite, int(self.x), int(self.y), BLANCO, TAM_PIXEL)

class UFO:
    def __init__(self):
        self.w = 14 * TAM_PIXEL
        self.h = 7 * TAM_PIXEL
        self.x = -self.w
        self.y = 50
        self.speed = 3
        self.activo = False
        self.timer = random.randint(300, 600)
        self.puntos = random.choice([50, 100, 150, 300])

    def actualizar(self):
        if not self.activo:
            self.timer -= 1
            if self.timer <= 0:
                self.activo = True
                self.x = -self.w
                self.y = 50
                self.puntos = random.choice([50, 100, 150, 300])
        else:
            self.x += self.speed
            if self.x > ANCHO:
                self.activo = False
                self.timer = random.randint(300, 600)

    def dibujar(self):
        if self.activo:
            dibujar_sprite(SPRITE_UFO, int(self.x), int(self.y), ROJO, TAM_PIXEL)

class Bala:
    def __init__(self, x, y, vy, es_jugador):
        self.x = float(x)
        self.y = float(y)
        self.vy = float(vy)
        self.es_jugador = es_jugador
        self.w = TAM_PIXEL
        self.h = TAM_PIXEL * 3
        self.activo = True

    def actualizar(self):
        self.y += self.vy
        if self.y < -20 or self.y > ALTO + 20:
            self.activo = False

    def dibujar(self):
        color = VERDE if self.es_jugador else BLANCO
        pygame.draw.rect(pantalla, color, (int(self.x), int(self.y), self.w, self.h))

class Bunker:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 14 * TAM_PIXEL
        self.h = 8 * TAM_PIXEL
        self.pixels = []
        for fila_idx, fila in enumerate(SPRITE_BUNKER):
            for col_idx, pixel in enumerate(fila):
                if pixel != 0:
                    self.pixels.append({
                        'x': x + col_idx * TAM_PIXEL,
                        'y': y + fila_idx * TAM_PIXEL,
                        'activo': True
                    })

    def dibujar(self):
        for pixel in self.pixels:
            if pixel['activo']:
                pygame.draw.rect(pantalla, VERDE, (pixel['x'], pixel['y'], TAM_PIXEL, TAM_PIXEL))

    def colision(self, x, y, w, h):
        for pixel in self.pixels:
            if pixel['activo']:
                if (x < pixel['x'] + TAM_PIXEL and x + w > pixel['x'] and
                    y < pixel['y'] + TAM_PIXEL and y + h > pixel['y']):
                    pixel['activo'] = False
                    return True
        return False

class Juego:
    def __init__(self):
        self.estado = 'menu'
        self.puntaje = 0
        self.high_score = 0
        try:
            with open('highscore_invaders.txt', 'r') as f: self.high_score = int(f.read())
        except: pass

        self.jugador = Jugador()
        self.aliens = []
        self.ufo = UFO()
        self.balas_jugador = []
        self.balas_alien = []
        self.bunkers = []
        self.particulas = []
        self.estrellas = [Estrella() for _ in range(100)]

        self.direccion_alien = 1
        self.velocidad_alien = 0.5
        self.velocidad_bajada = 20
        self.timer_bajada = 0

        self.crear_nivel()

    def crear_nivel(self):
        self.aliens = []
        self.balas_jugador = []
        self.balas_alien = []

        for fila in range(5):
            for col in range(11):
                tipo = 3 if fila == 0 else (2 if fila < 3 else 1)
                x = 100 + col * 50
                y = 150 + fila * 45
                alien = Alien(x, y, tipo, fila)
                self.aliens.append(alien)

        self.bunkers = []
        bunker_positions = [150, 300, 450, 600]
        for x in bunker_positions:
            self.bunkers.append(Bunker(x, ALTO - 180))

        self.direccion_alien = 1
        self.velocidad_alien = 0.5

    def crear_explosion(self, x, y, color, cantidad=15):
        for _ in range(cantidad):
            self.particulas.append(Particula(x, y, color))

    def actualizar(self):
        for p in self.particulas[:]:
            p.actualizar()
            if p.life <= 0: self.particulas.remove(p)

        if self.estado != 'jugando': return

        teclas = pygame.key.get_pressed()
        self.jugador.mover(teclas)
        self.jugador.actualizar()

        # Disparo rápido y constante - permite hasta 3 balas en pantalla
        if teclas[pygame.K_SPACE] and len(self.balas_jugador) < 3:
            self.jugador.disparar(self.balas_jugador)

        self.ufo.actualizar()

        movimiento_x = 0
        movimiento_y = 0

        aliens_restantes = len(self.aliens)
        if aliens_restantes > 0:
            factor_velocidad = 1 + (55 - aliens_restantes) * 0.05
            velocidad_actual = self.velocidad_alien * factor_velocidad
        else:
            velocidad_actual = self.velocidad_alien

        borde_alcanzado = False
        for alien in self.aliens:
            if (alien.x <= 10 and self.direccion_alien < 0) or \
               (alien.x + alien.w >= ANCHO - 10 and self.direccion_alien > 0):
                borde_alcanzado = True
                break

        if borde_alcanzado:
            self.direccion_alien *= -1
            movimiento_y = self.velocidad_bajada
            for alien in self.aliens:
                if alien.y + alien.h >= ALTO - 150:
                    self.estado = 'gameover'
                    if self.puntaje > self.high_score:
                        self.high_score = self.puntaje
                        with open('highscore_invaders.txt', 'w') as f: f.write(str(self.high_score))
        else:
            movimiento_x = velocidad_actual * self.direccion_alien

        for alien in self.aliens:
            alien.actualizar(movimiento_x, movimiento_y)

        if self.aliens and random.random() < 0.02:
            alien_shooter = random.choice(self.aliens)
            self.balas_alien.append(Bala(alien_shooter.x + alien_shooter.w//2,
                                        alien_shooter.y + alien_shooter.h, 4, False))

        for b in self.balas_jugador[:]:
            b.actualizar()
            if not b.activo: self.balas_jugador.remove(b)
        for b in self.balas_alien[:]:
            b.actualizar()
            if not b.activo: self.balas_alien.remove(b)

        for b in self.balas_jugador:
            if not b.activo: continue

            if self.ufo.activo and b.activo:
                if (b.x < self.ufo.x + self.ufo.w and b.x + b.w > self.ufo.x and
                    b.y < self.ufo.y + self.ufo.h and b.y + b.h > self.ufo.y):
                    b.activo = False
                    self.puntaje += self.ufo.puntos
                    self.crear_explosion(self.ufo.x + self.ufo.w//2, self.ufo.y + self.ufo.h//2, ROJO, 20)
                    self.ufo.activo = False
                    self.ufo.timer = random.randint(300, 600)
                    continue

            for alien in self.aliens[:]:
                if b.activo and (b.x < alien.x + alien.w and b.x + b.w > alien.x and
                                b.y < alien.y + alien.h and b.y + b.h > alien.y):
                    b.activo = False
                    self.puntaje += alien.puntos
                    self.crear_explosion(alien.x + alien.w//2, alien.y + alien.h//2, BLANCO, 15)
                    self.aliens.remove(alien)
                    break

            if b.activo:
                for bunker in self.bunkers:
                    if bunker.colision(b.x, b.y, b.w, b.h):
                        b.activo = False
                        break

        for b in self.balas_alien:
            if not b.activo: continue

            if (b.x < self.jugador.x + self.jugador.w and b.x + b.w > self.jugador.x and
                b.y < self.jugador.y + self.jugador.h and b.y + b.h > self.jugador.y):
                b.activo = False
                self.jugador.vidas -= 1
                self.crear_explosion(self.jugador.x + self.jugador.w//2, self.jugador.y + self.jugador.h//2, VERDE, 25)
                if self.jugador.vidas <= 0:
                    self.estado = 'gameover'
                    if self.puntaje > self.high_score:
                        self.high_score = self.puntaje
                        with open('highscore_invaders.txt', 'w') as f: f.write(str(self.high_score))
                continue

            for bunker in self.bunkers:
                if bunker.colision(b.x, b.y, b.w, b.h):
                    b.activo = False
                    break

        if len(self.aliens) == 0:
            self.crear_nivel()

    def dibujar(self):
        pantalla.fill(NEGRO)

        for e in self.estrellas: e.dibujar()

        if self.estado == 'menu':
            dibujar_texto_arcade("SPACE INVADERS", f_titulo, BLANCO, ANCHO//2, 200)
            dibujar_texto_arcade("ARCADE CLASSIC", f_texto, VERDE, ANCHO//2, 270)
            dibujar_texto_arcade(f"HIGH SCORE: {self.high_score}", f_texto, BLANCO, ANCHO//2, 330)
            dibujar_texto_arcade("PRESS ENTER TO START", f_pequena, CYAN, ANCHO//2, 450)
            dibujar_texto_arcade("← → MOVE  |  SPACE SHOOT", f_pequena, VERDE, ANCHO//2, 490)

        elif self.estado == 'jugando':
            dibujar_texto_arcade(f"SCORE<1>", f_marcador, BLANCO, 100, 10, centro=False)
            dibujar_texto_arcade(f"HI-SCORE", f_marcador, BLANCO, ANCHO//2 - 50, 10, centro=False)
            dibujar_texto_arcade(f"SCORE<2>", f_marcador, BLANCO, ANCHO - 150, 10, centro=False)
            dibujar_texto_arcade(f"{self.puntaje:04d}", f_marcador, BLANCO, 100, 35, centro=False)
            dibujar_texto_arcade(f"{self.high_score:04d}", f_marcador, BLANCO, ANCHO//2 - 50, 35, centro=False)
            dibujar_texto_arcade("0000", f_marcador, BLANCO, ANCHO - 150, 35, centro=False)

            self.jugador.dibujar()
            for alien in self.aliens: alien.dibujar()
            self.ufo.dibujar()
            for b in self.balas_jugador + self.balas_alien: b.dibujar()
            for bunker in self.bunkers: bunker.dibujar()
            for p in self.particulas: p.dibujar()

            dibujar_texto_arcade(f"{self.jugador.vidas}", f_marcador, VERDE, 20, ALTO - 30, centro=False)
            dibujar_sprite(SPRITE_JUGADOR, 50, ALTO - 35, VERDE, 2)
            dibujar_texto_arcade(f"CREDIT 00", f_marcador, BLANCO, ANCHO - 120, ALTO - 30, centro=False)

        elif self.estado == 'gameover':
            self.jugador.dibujar()
            for alien in self.aliens: alien.dibujar()
            for b in self.balas_jugador + self.balas_alien: b.dibujar()
            for bunker in self.bunkers: bunker.dibujar()
            for p in self.particulas: p.dibujar()

            s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            pantalla.blit(s, (0, 0))

            dibujar_texto_arcade("GAME OVER", f_titulo, ROJO, ANCHO//2, ALTO//2 - 50)
            dibujar_texto_arcade(f"SCORE: {self.puntaje}", f_texto, BLANCO, ANCHO//2, ALTO//2 + 20)
            dibujar_texto_arcade("PRESS ENTER", f_pequena, CYAN, ANCHO//2, ALTO//2 + 70)

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
                        juego.puntaje = 0
                        juego.jugador = Jugador()
                        juego.crear_nivel()
                    elif juego.estado == 'gameover':
                        juego.estado = 'jugando'
                        juego.puntaje = 0
                        juego.jugador = Jugador()
                        juego.crear_nivel()
        juego.actualizar()
        juego.dibujar()
        reloj.tick(FPS)

if __name__ == "__main__":
    main()
