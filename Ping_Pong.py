import pygame
import sys
import random

pygame.init()

ANCHO, ALTO = 800, 600
FPS = 60
PUNTOS_PARA_GANAR = 7

# Colores estrictamente blanco y negro
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (128, 128, 128)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("PING PONG ARCADE CLASSIC")
reloj = pygame.time.Clock()

# Fuente estilo arcade/pixelada
try:
    fuente_arcade = pygame.font.SysFont("couriernew", 48, bold=True)
    fuente_pequena = pygame.font.SysFont("couriernew", 24, bold=True)
    fuente_menu = pygame.font.SysFont("couriernew", 32, bold=True)
except:
    fuente_arcade = pygame.font.Font(None, 48)
    fuente_pequena = pygame.font.Font(None, 24)
    fuente_menu = pygame.font.Font(None, 32)

class PongArcade:
    def __init__(self):
        self.reset_juego()
        self.estado = "menu"  # menu, jugando, gameover
        self.modo = "1jugador"  # 1jugador o 2jugadores
        self.blink_timer = 0
        self.pausa_reinicio = 0  # Timer para pausa después de punto

    def reset_juego(self):
        # Paletas
        self.paddle_ancho = 12
        self.paddle_alto = 80
        self.paddle_vel = 6

        self.player1_y = ALTO // 2 - self.paddle_alto // 2
        self.player2_y = ALTO // 2 - self.paddle_alto // 2

        # Bola
        self.ball_size = 8
        self.ball_x = ANCHO // 2
        self.ball_y = ALTO // 2
        self.ball_vel_x = 5 * random.choice([1, -1])
        self.ball_vel_y = 3 * random.choice([1, -1])

        # Puntuación
        self.score1 = 0
        self.score2 = 0
        self.ganador = None
        self.pausa_reinicio = 0

    def reset_ball(self, direccion=1):
        self.ball_x = ANCHO // 2
        self.ball_y = ALTO // 2
        self.ball_vel_x = 5 * direccion
        self.ball_vel_y = 3 * random.choice([1, -1])
        self.pausa_reinicio = 60  # 1 segundo de pausa a 60 FPS

    def actualizar(self):
        self.blink_timer += 1

        # Manejar pausa después de punto
        if self.pausa_reinicio > 0:
            self.pausa_reinicio -= 1
            return

        if self.estado == "jugando":
            teclas = pygame.key.get_pressed()

            # Controles Jugador 1 (Izquierda) - FLECHAS ARRIBA/ABAJO
            if teclas[pygame.K_UP]:
                self.player1_y -= self.paddle_vel
            if teclas[pygame.K_DOWN]:
                self.player1_y += self.paddle_vel

            # Limitar paleta 1
            self.player1_y = max(0, min(ALTO - self.paddle_alto, self.player1_y))

            # Controles Jugador 2 (Derecha) - W/S o CPU
            if self.modo == "2jugadores":
                if teclas[pygame.K_w]:
                    self.player2_y -= self.paddle_vel
                if teclas[pygame.K_s]:
                    self.player2_y += self.paddle_vel
            else:
                # CPU simple
                centro_cpu = self.player2_y + self.paddle_alto // 2
                if centro_cpu < self.ball_y - 10:
                    self.player2_y += self.paddle_vel * 0.75
                elif centro_cpu > self.ball_y + 10:
                    self.player2_y -= self.paddle_vel * 0.75

            # Limitar paleta 2
            self.player2_y = max(0, min(ALTO - self.paddle_alto, self.player2_y))

            # Mover bola
            self.ball_x += self.ball_vel_x
            self.ball_y += self.ball_vel_y

            # Rebote arriba/abajo
            if self.ball_y <= 0 or self.ball_y >= ALTO - self.ball_size:
                self.ball_vel_y *= -1
                # Asegurar que la bola no se quede pegada
                if self.ball_y <= 0:
                    self.ball_y = 1
                else:
                    self.ball_y = ALTO - self.ball_size - 1

            # Colisión paleta 1
            if (self.ball_x <= 60 + self.paddle_ancho and
                self.ball_x >= 60 and
                self.ball_y + self.ball_size >= self.player1_y and
                self.ball_y <= self.player1_y + self.paddle_alto):
                self.ball_vel_x = abs(self.ball_vel_x) * 1.05
                self.ball_vel_x = min(self.ball_vel_x, 12)
                relativo = (self.player1_y + self.paddle_alto/2) - self.ball_y
                self.ball_vel_y = -relativo / (self.paddle_alto/2) * 5
                # Empujar la bola fuera de la paleta
                self.ball_x = 60 + self.paddle_ancho + 1

            # Colisión paleta 2
            if (self.ball_x + self.ball_size >= ANCHO - 60 - self.paddle_ancho and
                self.ball_x + self.ball_size <= ANCHO - 60 and
                self.ball_y + self.ball_size >= self.player2_y and
                self.ball_y <= self.player2_y + self.paddle_alto):
                self.ball_vel_x = -abs(self.ball_vel_x) * 1.05
                self.ball_vel_x = max(self.ball_vel_x, -12)
                relativo = (self.player2_y + self.paddle_alto/2) - self.ball_y
                self.ball_vel_y = -relativo / (self.paddle_alto/2) * 5
                # Empujar la bola fuera de la paleta
                self.ball_x = ANCHO - 60 - self.paddle_ancho - self.ball_size - 1

            # Punto - Jugador 2 anota (bola sale por izquierda)
            if self.ball_x < 0:
                self.score2 += 1
                if self.score2 >= PUNTOS_PARA_GANAR:
                    self.ganador = 2
                    self.estado = "gameover"
                else:
                    self.reset_ball(1)  # Bola va hacia la derecha (jugador 1 saca)

            # Punto - Jugador 1 anota (bola sale por derecha)
            elif self.ball_x > ANCHO:
                self.score1 += 1
                if self.score1 >= PUNTOS_PARA_GANAR:
                    self.ganador = 1
                    self.estado = "gameover"
                else:
                    self.reset_ball(-1)  # Bola va hacia la izquierda (jugador 2/CPU saca)

    def dibujar(self):
        # Fondo negro
        pantalla.fill(NEGRO)

        # Línea central discontinua
        for y in range(0, ALTO, 20):
            color = BLANCO if (y // 20) % 2 == 0 else NEGRO
            pygame.draw.rect(pantalla, color, (ANCHO//2 - 2, y, 4, 10))

        # Marcadores estilo digital
        texto1 = fuente_arcade.render(str(self.score1), True, BLANCO)
        texto2 = fuente_arcade.render(str(self.score2), True, BLANCO)
        pantalla.blit(texto1, (ANCHO//2 - 100, 30))
        pantalla.blit(texto2, (ANCHO//2 + 70, 30))

        # Paleta 1 (Izquierda)
        pygame.draw.rect(pantalla, BLANCO, (60, self.player1_y, self.paddle_ancho, self.paddle_alto))

        # Paleta 2 (Derecha)
        pygame.draw.rect(pantalla, BLANCO, (ANCHO - 60 - self.paddle_ancho, self.player2_y, self.paddle_ancho, self.paddle_alto))

        # Bola
        pygame.draw.rect(pantalla, BLANCO, (int(self.ball_x), int(self.ball_y), self.ball_size, self.ball_size))

        # MENÚ PRINCIPAL
        if self.estado == "menu":
            self.dibujar_menu()
        # GAME OVER
        elif self.estado == "gameover":
            self.dibujar_gameover()

        pygame.display.flip()

    def dibujar_menu(self):
        # Overlay semi-transparente
        s = pygame.Surface((ANCHO, ALTO))
        s.fill(NEGRO)
        pantalla.blit(s, (0, 0))

        # Título PING PONG
        titulo = fuente_arcade.render("PING PONG", True, BLANCO)
        pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 100))

        # Subtítulo
        subtitulo = fuente_pequena.render("ARCADE CLASSIC", True, GRIS)
        pantalla.blit(subtitulo, (ANCHO//2 - subtitulo.get_width()//2, 160))

        # Blink "PRESS ENTER TO START"
        if self.blink_timer % 60 < 30:
            texto_enter = fuente_menu.render("PRESS ENTER TO START", True, BLANCO)
            pantalla.blit(texto_enter, (ANCHO//2 - texto_enter.get_width()//2, 300))

        # Modo de juego
        modo_texto = f"MODE: {self.modo.upper()}"
        texto_modo = fuente_pequena.render(modo_texto, True, BLANCO)
        pantalla.blit(texto_modo, (ANCHO//2 - texto_modo.get_width()//2, 380))

        # Instrucciones
        if self.blink_timer % 60 < 30:
            if self.modo == "1jugador":
                instrucciones = [
                    "ARROWS - MOVE YOUR PADDLE",
                    "CPU - AUTO"
                ]
            else:
                instrucciones = [
                    "ARROWS - PLAYER 1 (LEFT)",
                    "W/S - PLAYER 2 (RIGHT)"
                ]
            for i, inst in enumerate(instrucciones):
                texto_inst = fuente_pequena.render(inst, True, GRIS)
                pantalla.blit(texto_inst, (ANCHO//2 - texto_inst.get_width()//2, 440 + i*30))

        # Cambiar modo
        texto_modo_cambio = fuente_pequena.render("PRESS M TO CHANGE MODE", True, GRIS)
        pantalla.blit(texto_modo_cambio, (ANCHO//2 - texto_modo_cambio.get_width()//2, 520))

    def dibujar_gameover(self):
        # Overlay
        s = pygame.Surface((ANCHO, ALTO))
        s.fill(NEGRO)
        pantalla.blit(s, (0, 0))

        # Mensaje de victoria/derrota
        if self.ganador == 1:
            ganador_txt = "PLAYER 1 WINS!" if self.modo == "2jugadores" else "YOU WIN!"
        else:
            ganador_txt = "PLAYER 2 WINS!" if self.modo == "2jugadores" else "CPU WINS!"

        texto_ganador = fuente_arcade.render(ganador_txt, True, BLANCO)
        pantalla.blit(texto_ganador, (ANCHO//2 - texto_ganador.get_width()//2, 200))

        # Marcador final
        marcador = f"{self.score1} - {self.score2}"
        texto_marcador = fuente_menu.render(marcador, True, GRIS)
        pantalla.blit(texto_marcador, (ANCHO//2 - texto_marcador.get_width()//2, 280))

        # Blink "PRESS ENTER TO PLAY AGAIN"
        if self.blink_timer % 60 < 30:
            texto_restart = fuente_menu.render("PRESS ENTER TO PLAY AGAIN", True, BLANCO)
            pantalla.blit(texto_restart, (ANCHO//2 - texto_restart.get_width()//2, 380))

        # Volver al menú
        texto_menu = fuente_pequena.render("PRESS ESC FOR MENU", True, GRIS)
        pantalla.blit(texto_menu, (ANCHO//2 - texto_menu.get_width()//2, 460))

def main():
    juego = PongArcade()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if juego.estado == "menu":
                    if evento.key == pygame.K_RETURN:
                        juego.reset_juego()
                        juego.estado = "jugando"
                    if evento.key == pygame.K_m:
                        if juego.modo == "1jugador":
                            juego.modo = "2jugadores"
                        else:
                            juego.modo = "1jugador"
                    if evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                elif juego.estado == "jugando":
                    if evento.key == pygame.K_ESCAPE:
                        juego.estado = "menu"
                    if evento.key == pygame.K_p:
                        juego.estado = "menu"

                elif juego.estado == "gameover":
                    if evento.key == pygame.K_RETURN:
                        juego.reset_juego()
                        juego.estado = "jugando"
                    if evento.key == pygame.K_ESCAPE:
                        juego.estado = "menu"

        juego.actualizar()
        juego.dibujar()
        reloj.tick(FPS)

if __name__ == "__main__":
    main()
