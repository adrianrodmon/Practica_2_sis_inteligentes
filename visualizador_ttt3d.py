import pygame

class Visualizador3D:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((700, 700))
        pygame.display.set_caption("3D TicTacToe (Vista por capas)")
        self.clock = pygame.time.Clock()

        self.cell = 100
        self.offset_x = 150
        self.offset_y = 100

        self.capa_actual = 1  # 🔥 capa Z activa (1–4)

    # ─── DIBUJO ─────────────────────────────

    def actualizar(self, estado):
        self.render(estado)

    def render(self, estado):
        self.screen.fill((25, 25, 35))

        font = pygame.font.SysFont(None, 36)

        # texto de capa
        texto = font.render(f"Capa Z = {self.capa_actual} (teclas 1-4)", True, (255,255,255))
        self.screen.blit(texto, (200, 20))

        # dibujar grilla 4x4 de la capa actual
        for x in range(4):
            for y in range(4):

                px = self.offset_x + x * self.cell
                py = self.offset_y + y * self.cell

                pygame.draw.rect(
                    self.screen,
                    (100,100,100),
                    (px, py, self.cell-5, self.cell-5),
                    2
                )

        # dibujar fichas SOLO de esa capa
        for (x, y, z), v in estado.tablero.items():

            if z != self.capa_actual:
                continue

            px = self.offset_x + (x-1)*self.cell + self.cell//2
            py = self.offset_y + (y-1)*self.cell + self.cell//2

            color = (0,255,0) if v == 'X' else (255,0,0)

            pygame.draw.circle(self.screen, color, (px, py), 25)

        pygame.display.flip()

    # ─── INPUT ─────────────────────────────

    def esperar_movida(self, estado):
        while True:
            for ev in pygame.event.get():

                if ev.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                # cambiar capa con teclado
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_1:
                        self.capa_actual = 1
                    if ev.key == pygame.K_2:
                        self.capa_actual = 2
                    if ev.key == pygame.K_3:
                        self.capa_actual = 3
                    if ev.key == pygame.K_4:
                        self.capa_actual = 4

                # click
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = ev.pos

                    for x in range(4):
                        for y in range(4):

                            px = self.offset_x + x * self.cell
                            py = self.offset_y + y * self.cell

                            rect = pygame.Rect(px, py, self.cell-5, self.cell-5)

                            if rect.collidepoint(mx, my):
                                mov = (x+1, y+1, self.capa_actual)

                                if mov in estado.movidas:
                                    return mov

            self.actualizar(estado)
            self.clock.tick(60)

    def _handle_event(self, ev):
        pass