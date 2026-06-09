import pygame
import sys
import math
import random
import struct

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

ANCHO, ALTO = 900, 700
FPS = 60
NIVELES_MAX = 10
VIDAS_INICIALES = 3
VIDAS_EXTRA_CADA = 10000

C = {
    'negro': (0, 0, 0),
    'blanco': (255, 255, 255),
    'rojo': (255, 0, 0),
    'amarillo': (255, 255, 0)
}

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("ASTEROIDS - SUPERVIVENCIA EXTREMA")
reloj = pygame.time.Clock()

f_titulo = pygame.font.SysFont("consolas", 72, bold=False)
f_txt = pygame.font.SysFont("consolas", 24, bold=False)
f_pequena = pygame.font.SysFont("consolas", 16)

def generar_sonido_disparo():
    sample_rate = 44100
    duracion = 0.12
    num_samples = int(sample_rate * duracion)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        frecuencia = 1500 - (t * 8000)
        valor = int(12000 * math.sin(2 * math.pi * frecuencia * t) * math.exp(-t * 18))
        samples.append(valor)
    return crear_sonido_desde_samples(samples, sample_rate)

def generar_sonido_golpe_asteroide():
    sample_rate = 44100
    duracion = 0.25
    num_samples = int(sample_rate * duracion)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        ruido = random.uniform(-1, 1)
        envolvente = math.exp(-t * 12)
        valor1 = int(20000 * ruido * envolvente)
        valor2 = int(8000 * math.sin(2 * math.pi * 100 * t) * envolvente)
        valor = valor1 + valor2
        samples.append(valor)
    return crear_sonido_desde_samples(samples, sample_rate)

def generar_sonido_explosion_nave():
    sample_rate = 44100
    duracion = 1.0
    num_samples = int(sample_rate * duracion)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        ruido = random.uniform(-1, 1)
        envolvente = math.exp(-t * 3)
        freq = 300 * math.exp(-t * 2)
        valor1 = int(22000 * ruido * envolvente)
        valor2 = int(12000 * math.sin(2 * math.pi * freq * t) * envolvente)
        valor3 = int(6000 * math.sin(2 * math.pi * (freq * 0.5) * t) * envolvente)
        valor = valor1 + valor2 + valor3
        samples.append(valor)
    return crear_sonido_desde_samples(samples, sample_rate)

def generar_sonido_propulsion():
    sample_rate = 44100
    duracion = 0.05
    num_samples = int(sample_rate * duracion)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        valor = int(8000 * math.sin(2 * math.pi * 150 * t) * math.exp(-t * 25))
        samples.append(valor)
    return crear_sonido_desde_samples(samples, sample_rate)

def crear_sonido_desde_samples(samples, sample_rate):
    sample_width = 2
    channels = 2
    wave_data = b''
    for sample in samples:
        sample = max(-32768, min(32767, sample))
        wave_data += struct.pack('<h', sample)
        wave_data += struct.pack('<h', sample)
    sound = pygame.mixer.Sound(buffer=wave_data)
    return sound

sonido_disparo = generar_sonido_disparo()
sonido_golpe_asteroide = generar_sonido_golpe_asteroide()
sonido_explosion_nave = generar_sonido_explosion_nave()
sonido_propulsion = generar_sonido_propulsion()

def distancia(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def envolver(obj):
    if obj.x < -20: obj.x = ANCHO + 20
    if obj.x > ANCHO + 20: obj.x = -20
    if obj.y < -20: obj.y = ALTO + 20
    if obj.y > ALTO + 20: obj.y = -20

class AsteroideMenu:
    def __init__(self):
        self.x = random.randint(0, ANCHO)
        self.y = random.randint(0, ALTO)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.tamano = random.choice([15, 25, 35])
        self.rotacion = random.uniform(0, 360)
        self.vel_rotacion = random.uniform(-0.5, 0.5)
        self.vertices = []
        num_puntos = random.randint(8, 12)
        for i in range(num_puntos):
            angulo = (i / num_puntos) * math.pi * 2
            radio_var = self.tamano * random.uniform(0.7, 1.3)
            self.vertices.append((math.cos(angulo) * radio_var, math.sin(angulo) * radio_var))

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.rotacion += self.vel_rotacion
        if self.x < -50: self.x = ANCHO + 50
        if self.x > ANCHO + 50: self.x = -50
        if self.y < -50: self.y = ALTO + 50
        if self.y > ALTO + 50: self.y = -50

    def dibujar(self, superficie):
        puntos_rotados = []
        rad_rot = math.radians(self.rotacion)
        for vx, vy in self.vertices:
            rx = vx * math.cos(rad_rot) - vy * math.sin(rad_rot)
            ry = vx * math.sin(rad_rot) + vy * math.cos(rad_rot)
            puntos_rotados.append((self.x + rx, self.y + ry))
        pygame.draw.polygon(superficie, C['blanco'], puntos_rotados, 2)

class Estrella:
    def __init__(self):
        self.x = random.randint(0, ANCHO)
        self.y = random.randint(0, ALTO)
        self.size = random.uniform(0.5, 1.5)
        self.alpha = random.randint(100, 255)

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, (self.alpha, self.alpha, self.alpha),
                          (int(self.x), int(self.y)), int(self.size))

class Particula:
    def __init__(self, x, y, vx, vy, size, life, color=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.life = life
        self.max_life = life
        self.color = color if color else C['blanco']

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size *= 0.96

    def dibujar(self, superficie):
        if self.life > 0:
            pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), int(self.size))

class LineaPropulsion:
    def __init__(self, x, y, angulo):
        self.x = x
        self.y = y
        self.angulo = angulo + math.pi + random.uniform(-0.4, 0.4)
        self.velocidad = random.uniform(4, 8)
        self.vx = math.cos(self.angulo) * self.velocidad
        self.vy = math.sin(self.angulo) * self.velocidad
        self.life = 20
        self.max_life = 20
        self.length = random.randint(8, 20)

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def dibujar(self, superficie):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            x_final = self.x - math.cos(self.angulo) * self.length
            y_final = self.y - math.sin(self.angulo) * self.length
            pygame.draw.line(superficie, (alpha, alpha, alpha),
                           (int(self.x), int(self.y)), (int(x_final), int(y_final)), 2)

class Nave:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = ANCHO // 2
        self.y = ALTO // 2
        self.vx = 0
        self.vy = 0
        self.angulo = -90
        self.radio = 15
        self.invulnerable = 120
        self.vivo = True
        self.propulsando = False

    def rotar(self, dir):
        self.angulo += dir * 5

    def propulsar(self, adelante=True):
        rad = math.radians(self.angulo)
        fuerza = 0.15 if adelante else -0.1
        self.vx += math.cos(rad) * fuerza
        self.vy += math.sin(rad) * fuerza
        if adelante:
            self.propulsando = True
            px = self.x - math.cos(rad) * 15
            py = self.y - math.sin(rad) * 15
            for _ in range(3):
                juego.lineas_propulsion.append(LineaPropulsion(px, py, self.angulo))
            if random.random() < 0.3:
                sonido_propulsion.play()
        else:
            self.propulsando = False

    def actualizar(self):
        if not self.vivo:
            return
        if self.invulnerable > 0:
            self.invulnerable -= 1
        if not self.propulsando:
            self.propulsando = False
        self.vx *= 0.99
        self.vy *= 0.99
        self.x += self.vx
        self.y += self.vy
        envolver(self)

    def dibujar(self, superficie):
        if not self.vivo:
            return
        if self.invulnerable > 0 and (self.invulnerable // 5) % 2 == 0:
            return
        rad = math.radians(self.angulo)
        p1 = (self.x + math.cos(rad) * 18, self.y + math.sin(rad) * 18)
        p2 = (self.x + math.cos(rad + 2.5) * 12, self.y + math.sin(rad + 2.5) * 12)
        p3 = (self.x + math.cos(rad - 2.5) * 12, self.y + math.sin(rad - 2.5) * 12)
        pygame.draw.polygon(superficie, C['blanco'], [p1, p2, p3], 2)

class Asteroide:
    def __init__(self, x, y, tamano, vx=None, vy=None, nivel=1):
        self.x = x
        self.y = y
        self.tamano = tamano
        self.radio = [15, 25, 40][tamano - 1]
        velocidad_base = 0.8 + (nivel * 0.2)
        multiplicador_tamano = [3.0, 1.8, 1.0][tamano - 1]
        velocidad_final = velocidad_base * multiplicador_tamano
        if vx is None:
            angulo = random.uniform(0, math.pi * 2)
            self.vx = math.cos(angulo) * velocidad_final
            self.vy = math.sin(angulo) * velocidad_final
        else:
            self.vx = vx
            self.vy = vy
        self.rotacion = 0
        self.vel_rotacion = random.uniform(-1, 1)
        self.vertices = []
        num_puntos = random.randint(8, 12)
        for i in range(num_puntos):
            angulo = (i / num_puntos) * math.pi * 2
            radio_var = self.radio * random.uniform(0.7, 1.3)
            self.vertices.append((math.cos(angulo) * radio_var, math.sin(angulo) * radio_var))

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.rotacion += self.vel_rotacion
        envolver(self)

    def dibujar(self, superficie):
        puntos_rotados = []
        rad_rot = math.radians(self.rotacion)
        for vx, vy in self.vertices:
            rx = vx * math.cos(rad_rot) - vy * math.sin(rad_rot)
            ry = vx * math.sin(rad_rot) + vy * math.cos(rad_rot)
            puntos_rotados.append((self.x + rx, self.y + ry))
        pygame.draw.polygon(superficie, C['blanco'], puntos_rotados, 2)

class PlatilloGrande:
    def __init__(self):
        self.x = random.choice([-30, ANCHO + 30])
        self.y = random.randint(50, ALTO - 50)
        self.vx = 2 if self.x < 0 else -2
        self.vy = random.uniform(-0.5, 0.5)
        self.radio = 20
        self.timer_disparo = random.randint(100, 200)
        self.puntos = 200
        self.angulo = 0

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.angulo += 0.05
        if self.y < 50 or self.y > ALTO - 50:
            self.vy *= -1
        self.timer_disparo -= 1

    def dibujar(self, superficie):
        x, y = int(self.x), int(self.y)
        r = self.radio
        pygame.draw.ellipse(superficie, C['blanco'],
                          (x - r, y - r//3, r * 2, r//1.5), 2)
        pygame.draw.arc(superficie, C['blanco'],
                       (x - r//2, y - r, r, r),
                       math.pi, 0, 2)
        pygame.draw.line(superficie, C['blanco'],
                        (x - r, y), (x + r, y), 1)
        for i in range(-1, 2):
            lx = x + i * (r // 2)
            ly = y + 2
            pygame.draw.circle(superficie, C['amarillo'], (lx, ly), 2)

class PlatilloPequeno:
    def __init__(self, nave_x, nave_y):
        self.x = random.choice([-30, ANCHO + 30])
        self.y = random.choice([-30, ALTO + 30])
        self.radio = 12
        self.velocidad = 3
        self.timer_disparo = random.randint(60, 120)
        self.puntos = 500
        self.nave_x = nave_x
        self.nave_y = nave_y
        self.angulo = 0

    def actualizar(self, nave_x, nave_y):
        dx = nave_x - self.x
        dy = nave_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            self.x += (dx / dist) * self.velocidad
            self.y += (dy / dist) * self.velocidad
            self.angulo = math.atan2(dy, dx)
        self.timer_disparo -= 1

    def dibujar(self, superficie):
        x, y = int(self.x), int(self.y)
        r = self.radio
        cos_a = math.cos(self.angulo)
        sin_a = math.sin(self.angulo)
        p1 = (x + cos_a * r, y + sin_a * r)
        p2 = (x - cos_a * r * 0.7 + sin_a * r * 0.5,
              y - sin_a * r * 0.7 - cos_a * r * 0.5)
        p3 = (x - cos_a * r * 0.7 - sin_a * r * 0.5,
              y - sin_a * r * 0.7 + cos_a * r * 0.5)
        pygame.draw.polygon(superficie, C['blanco'], [p1, p2, p3], 2)
        pygame.draw.circle(superficie, C['rojo'], (x, y), r // 3, 1)
        p4 = (x - cos_a * r * 0.5 + sin_a * r * 0.3,
              y - sin_a * r * 0.5 - cos_a * r * 0.3)
        p5 = (x - cos_a * r * 0.5 - sin_a * r * 0.3,
              y - sin_a * r * 0.5 + cos_a * r * 0.3)
        pygame.draw.line(superficie, C['amarillo'], p4, p5, 1)

class Bala:
    def __init__(self, x, y, vx, vy, es_jugador=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.vida = 60
        self.es_jugador = es_jugador

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vida -= 1
        envolver(self)

    def dibujar(self, superficie):
        color = C['blanco'] if self.es_jugador else C['amarillo']
        pygame.draw.circle(superficie, color, (int(self.x), int(self.y)), 3)

class AsteroidsGame:
    def __init__(self):
        self.nave = Nave()
        self.asteroides = []
        self.balas = []
        self.particulas = []
        self.lineas_propulsion = []
        self.platillos_grandes = []
        self.platillos_pequenos = []
        self.puntaje = 0
        self.vidas = VIDAS_INICIALES
        self.vidas_extra_acumuladas = 0
        self.nivel = 1
        self.estado = "menu"
        self.asteroides_menu = [AsteroideMenu() for _ in range(15)]
        self.estrellas = [Estrella() for _ in range(50)]
        self.titulo_y = 0
        self.titulo_dir = 1
        self.record = self.cargar_record()
        self.ultimo_disparo = 0
        self.flash_alpha = 0
        self.crear_oleada()

    def cargar_record(self):
        try:
            with open('record_asteroids.txt', 'r') as f:
                return int(f.read())
        except:
            return 0

    def guardar_record(self):
        if self.puntaje > self.record:
            self.record = self.puntaje
            with open('record_asteroids.txt', 'w') as f:
                f.write(str(self.record))

    def crear_oleada(self):
        self.asteroides = []
        self.platillos_grandes = []
        self.platillos_pequenos = []

        cantidad_asteroides = 3 + self.nivel * 2

        for _ in range(cantidad_asteroides):
            while True:
                x = random.randint(0, ANCHO)
                y = random.randint(0, ALTO)
                if distancia(x, y, self.nave.x, self.nave.y) > 150:
                    break
            self.asteroides.append(Asteroide(x, y, 3, nivel=self.nivel))

        if self.nivel >= 2 and self.nivel % 2 == 0:
            self.platillos_grandes.append(PlatilloGrande())

        if self.nivel >= 3 and self.nivel % 3 == 0:
            self.platillos_pequenos.append(PlatilloPequeno(self.nave.x, self.nave.y))

    def crear_explosion(self, x, y, cantidad=30):
        for _ in range(cantidad):
            angulo = random.uniform(0, math.pi * 2)
            velocidad = random.uniform(2, 6)
            vx = math.cos(angulo) * velocidad
            vy = math.sin(angulo) * velocidad
            size = random.randint(2, 5)
            life = random.randint(25, 50)
            self.particulas.append(Particula(x, y, vx, vy, size, life))

    def crear_explosion_nave(self, x, y):
        for _ in range(80):
            angulo = random.uniform(0, math.pi * 2)
            velocidad = random.uniform(3, 10)
            vx = math.cos(angulo) * velocidad
            vy = math.sin(angulo) * velocidad
            size = random.randint(2, 8)
            life = random.randint(40, 80)
            self.particulas.append(Particula(x, y, vx, vy, size, life))
        for _ in range(20):
            angulo = random.uniform(0, math.pi * 2)
            velocidad = random.uniform(1, 4)
            vx = math.cos(angulo) * velocidad
            vy = math.sin(angulo) * velocidad
            size = random.randint(5, 12)
            life = random.randint(60, 100)
            self.particulas.append(Particula(x, y, vx, vy, size, life))
        self.flash_alpha = 255

    def disparar(self):
        if self.nave.vivo:
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - self.ultimo_disparo >= 150:
                rad = math.radians(self.nave.angulo)
                bx = self.nave.x + math.cos(rad) * 15
                by = self.nave.y + math.sin(rad) * 15
                bvx = math.cos(rad) * 12 + self.nave.vx
                bvy = math.sin(rad) * 12 + self.nave.vy
                self.balas.append(Bala(bx, by, bvx, bvy, es_jugador=True))
                sonido_disparo.play()
                self.ultimo_disparo = tiempo_actual

    def actualizar(self):
        if self.flash_alpha > 0:
            self.flash_alpha -= 8
            if self.flash_alpha < 0:
                self.flash_alpha = 0

        for p in self.particulas[:]:
            p.actualizar()
            if p.life <= 0:
                self.particulas.remove(p)

        for l in self.lineas_propulsion[:]:
            l.actualizar()
            if l.life <= 0:
                self.lineas_propulsion.remove(l)

        if self.estado == "menu":
            for a in self.asteroides_menu:
                a.actualizar()
            self.titulo_y += 0.5 * self.titulo_dir
            if abs(self.titulo_y) > 5:
                self.titulo_dir *= -1
            return

        if self.estado != "jugando":
            return

        self.nave.actualizar()

        for b in self.balas[:]:
            b.actualizar()
            if b.vida <= 0:
                self.balas.remove(b)

        for a in self.asteroides:
            a.actualizar()

        for pg in self.platillos_grandes:
            pg.actualizar()

        for pp in self.platillos_pequenos:
            pp.actualizar(self.nave.x, self.nave.y)

        for b in self.balas[:]:
            if b.es_jugador:
                for a in self.asteroides[:]:
                    if distancia(b.x, b.y, a.x, a.y) < a.radio:
                        self.crear_explosion(a.x, a.y, 35)
                        sonido_golpe_asteroide.play()
                        pts = {3: 20, 2: 50, 1: 100}
                        self.puntaje += pts[a.tamano]
                        if a.tamano > 1:
                            for _ in range(2):
                                self.asteroides.append(Asteroide(
                                    a.x, a.y, a.tamano - 1, nivel=self.nivel
                                ))
                        self.asteroides.remove(a)
                        if b in self.balas:
                            self.balas.remove(b)
                        break

                for pg in self.platillos_grandes[:]:
                    if distancia(b.x, b.y, pg.x, pg.y) < pg.radio:
                        self.crear_explosion(pg.x, pg.y, 25)
                        sonido_golpe_asteroide.play()
                        self.puntaje += pg.puntos
                        self.platillos_grandes.remove(pg)
                        if b in self.balas:
                            self.balas.remove(b)
                        break

                for pp in self.platillos_pequenos[:]:
                    if distancia(b.x, b.y, pp.x, pp.y) < pp.radio:
                        self.crear_explosion(pp.x, pp.y, 25)
                        sonido_golpe_asteroide.play()
                        self.puntaje += pp.puntos
                        self.platillos_pequenos.remove(pp)
                        if b in self.balas:
                            self.balas.remove(b)
                        break
            else:
                if self.nave.invulnerable <= 0 and self.nave.vivo:
                    if distancia(b.x, b.y, self.nave.x, self.nave.y) < self.nave.radio:
                        self.nave.vivo = False
                        self.crear_explosion_nave(self.nave.x, self.nave.y)
                        sonido_explosion_nave.play()
                        self.vidas -= 1
                        if self.vidas > 0:
                            pygame.time.delay(2000)
                            self.nave.reset()
                        else:
                            self.guardar_record()
                            self.estado = "gameover"
                        if b in self.balas:
                            self.balas.remove(b)
                        break

        if self.nave.invulnerable <= 0 and self.nave.vivo:
            for a in self.asteroides:
                if distancia(self.nave.x, self.nave.y, a.x, a.y) < a.radio + self.nave.radio - 5:
                    self.nave.vivo = False
                    self.crear_explosion_nave(self.nave.x, self.nave.y)
                    sonido_explosion_nave.play()
                    self.vidas -= 1
                    if self.vidas > 0:
                        pygame.time.delay(2000)
                        self.nave.reset()
                    else:
                        self.guardar_record()
                        self.estado = "gameover"
                    break

        for pg in self.platillos_grandes:
            if pg.timer_disparo <= 0:
                angulo = random.uniform(0, math.pi * 2)
                bvx = math.cos(angulo) * 5
                bvy = math.sin(angulo) * 5
                self.balas.append(Bala(pg.x, pg.y, bvx, bvy, es_jugador=False))
                pg.timer_disparo = random.randint(100, 200)

        for pp in self.platillos_pequenos:
            if pp.timer_disparo <= 0:
                dx = self.nave.x - pp.x
                dy = self.nave.y - pp.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist > 0:
                    bvx = (dx / dist) * 6
                    bvy = (dy / dist) * 6
                    self.balas.append(Bala(pp.x, pp.y, bvx, bvy, es_jugador=False))
                pp.timer_disparo = random.randint(60, 120)

        vidas_ganadas = self.puntaje // VIDAS_EXTRA_CADA
        if vidas_ganadas > self.vidas_extra_acumuladas:
            self.vidas += 1
            self.vidas_extra_acumuladas = vidas_ganadas

        if len(self.asteroides) == 0 and len(self.platillos_grandes) == 0 and len(self.platillos_pequenos) == 0:
            if self.nivel < NIVELES_MAX:
                self.nivel += 1
                self.nave.reset()
                self.crear_oleada()
            else:
                self.guardar_record()
                self.estado = "victoria"

    def dibujar(self):
        pantalla.fill(C['negro'])

        if self.estado == "menu":
            for estrella in self.estrellas:
                estrella.dibujar(pantalla)
            for a in self.asteroides_menu:
                a.dibujar(pantalla)
            titulo_texto = "ASTEROIDS"
            titulo_surf = f_titulo.render(titulo_texto, True, C['blanco'])
            titulo_rect = titulo_surf.get_rect(center=(ANCHO//2, ALTO//2 - 60 + self.titulo_y))
            pantalla.blit(titulo_surf, titulo_rect.topleft)
            sub_texto = "PRESS ENTER TO PLAY"
            sub_surf = f_txt.render(sub_texto, True, C['blanco'])
            sub_rect = sub_surf.get_rect(center=(ANCHO//2, ALTO//2 + 20))
            pantalla.blit(sub_surf, sub_rect.topleft)
            record_texto = f"RECORD: {self.record}"
            record_surf = f_pequena.render(record_texto, True, C['blanco'])
            record_rect = record_surf.get_rect(center=(ANCHO//2, ALTO//2 + 60))
            pantalla.blit(record_surf, record_rect.topleft)
            controles = ["← → : ROTAR", "↑ : PROPULSAR", "↓ : FRENAR", "ESPACIO : DISPARAR"]
            for i, txt in enumerate(controles):
                ctrl_surf = f_pequena.render(txt, True, C['blanco'])
                pantalla.blit(ctrl_surf, (ANCHO//2 - 80, ALTO//2 + 110 + i*20))

        elif self.estado == "jugando":
            for a in self.asteroides:
                a.dibujar(pantalla)
            for pg in self.platillos_grandes:
                pg.dibujar(pantalla)
            for pp in self.platillos_pequenos:
                pp.dibujar(pantalla)
            for b in self.balas:
                b.dibujar(pantalla)
            for p in self.particulas:
                p.dibujar(pantalla)
            for l in self.lineas_propulsion:
                l.dibujar(pantalla)
            self.nave.dibujar(pantalla)
            puntaje_texto = f"SCORE: {self.puntaje}"
            puntaje_surf = f_pequena.render(puntaje_texto, True, C['blanco'])
            pantalla.blit(puntaje_surf, (20, 20))
            vidas_texto = f"LIVES: {self.vidas}"
            vidas_surf = f_pequena.render(vidas_texto, True, C['blanco'])
            pantalla.blit(vidas_surf, (ANCHO - 100, 20))
            nivel_texto = f"LEVEL {self.nivel}/{NIVELES_MAX}"
            nivel_surf = f_pequena.render(nivel_texto, True, C['blanco'])
            pantalla.blit(nivel_surf, (ANCHO//2 - 40, 20))
            if self.nave.invulnerable > 0 and (self.nave.invulnerable // 5) % 2 == 0:
                pygame.draw.circle(pantalla, C['blanco'], (int(self.nave.x), int(self.nave.y)), 20, 1)

        elif self.estado == "gameover":
            for a in self.asteroides:
                a.dibujar(pantalla)
            for p in self.particulas:
                p.dibujar(pantalla)
            gameover_texto = "GAME OVER"
            gameover_surf = f_titulo.render(gameover_texto, True, C['blanco'])
            gameover_rect = gameover_surf.get_rect(center=(ANCHO//2, ALTO//2 - 80))
            pantalla.blit(gameover_surf, gameover_rect.topleft)
            score_texto = f"FINAL SCORE: {self.puntaje}"
            score_surf = f_txt.render(score_texto, True, C['blanco'])
            score_rect = score_surf.get_rect(center=(ANCHO//2, ALTO//2 - 20))
            pantalla.blit(score_surf, score_rect.topleft)
            record_texto = f"RECORD: {self.record}"
            record_surf = f_txt.render(record_texto, True, C['blanco'])
            record_rect = record_surf.get_rect(center=(ANCHO//2, ALTO//2 + 20))
            pantalla.blit(record_surf, record_rect.topleft)
            restart_texto = "PRESS ENTER TO RESTART"
            restart_surf = f_txt.render(restart_texto, True, C['blanco'])
            restart_rect = restart_surf.get_rect(center=(ANCHO//2, ALTO//2 + 70))
            pantalla.blit(restart_surf, restart_rect.topleft)

        elif self.estado == "victoria":
            for p in self.particulas:
                p.dibujar(pantalla)
            victoria_texto = "VICTORY!"
            victoria_surf = f_titulo.render(victoria_texto, True, C['blanco'])
            victoria_rect = victoria_surf.get_rect(center=(ANCHO//2, ALTO//2 - 80))
            pantalla.blit(victoria_surf, victoria_rect.topleft)
            score_texto = f"FINAL SCORE: {self.puntaje}"
            score_surf = f_txt.render(score_texto, True, C['blanco'])
            score_rect = score_surf.get_rect(center=(ANCHO//2, ALTO//2 - 20))
            pantalla.blit(score_surf, score_rect.topleft)
            record_texto = f"RECORD: {self.record}"
            record_surf = f_txt.render(record_texto, True, C['blanco'])
            record_rect = record_surf.get_rect(center=(ANCHO//2, ALTO//2 + 20))
            pantalla.blit(record_surf, record_rect.topleft)
            restart_texto = "PRESS ENTER TO PLAY AGAIN"
            restart_surf = f_txt.render(restart_texto, True, C['blanco'])
            restart_rect = restart_surf.get_rect(center=(ANCHO//2, ALTO//2 + 70))
            pantalla.blit(restart_surf, restart_rect.topleft)

        if self.flash_alpha > 0:
            flash_surf = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, self.flash_alpha))
            pantalla.blit(flash_surf, (0, 0))

        pygame.display.flip()

def main():
    global juego
    juego = AsteroidsGame()

    while True:
        dt = reloj.tick(FPS)
        eventos = pygame.event.get()

        for e in eventos:
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    if juego.estado == "menu":
                        juego = AsteroidsGame()
                        juego.estado = "jugando"
                    elif juego.estado in ["gameover", "victoria"]:
                        juego = AsteroidsGame()
                        juego.estado = "jugando"

        if juego.estado == "jugando" and juego.nave.vivo:
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                juego.nave.rotar(-1)
            if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                juego.nave.rotar(1)
            if teclas[pygame.K_UP] or teclas[pygame.K_w]:
                juego.nave.propulsar(adelante=True)
            else:
                juego.nave.propulsando = False
            if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
                juego.nave.propulsar(adelante=False)
            if teclas[pygame.K_SPACE]:
                juego.disparar()

        juego.actualizar()
        juego.dibujar()

if __name__ == "__main__":
    main()
