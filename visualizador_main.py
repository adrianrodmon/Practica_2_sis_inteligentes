import pygame
import sys

from AgenteTresEnRaya import AgenteTresEnRaya
from Tablero import Tablero
from AgenteJugador import ElEstado
from visualizador_ttt3d import Visualizador3D


# ─── HUMANO VISUAL ─────────────────────────

class HumanoVisual(AgenteTresEnRaya):

    def __init__(self, n=4, visualizador=None):
        super().__init__(n)
        self.vis = visualizador
        self._reset_flag = False

    def programa(self):
        movida = self.vis.esperar_movida(self.estado)

        if movida == '__reset__':
            self._reset_flag = True
            self.set_acciones(self.estado.movidas[0] if self.estado.movidas else None)
            return

        self._reset_flag = False
        self.set_acciones(movida)

    def mostrar(self, estado):
        self.vis.actualizar(estado)


# ─── TABLERO VISUAL ─────────────────────────

class TableroVisual(Tablero):

    def __init__(self, n=4):
        super().__init__(n)
        self.vis = Visualizador3D()
        self._humano = None
        self._ia = None

    def insertar_humano(self, humano):
        humano.vis = self.vis
        self._humano = humano
        self.insertar(humano)

    def insertar_ia(self, ia):
        self._ia = ia
        self.insertar(ia)

    def get_percepciones(self, agente):
        agente.estado = self.juegoActual
        self.vis.actualizar(self.juegoActual)

        if agente.estado.movidas:
            agente.programa()

    def ejecutar(self, agente):

        if isinstance(agente, HumanoVisual) and agente._reset_flag:
            self._reiniciar()
            return

        self.juegoActual = agente.getResultado(self.juegoActual, agente.get_acciones())
        self.vis.actualizar(self.juegoActual)

        if self.juegoActual.get_utilidad != 0:
            ganador = 'X' if self.juegoActual.get_utilidad == 1 else 'O'
            print("GANÓ:", ganador)
            pygame.time.wait(2000)
            self._reiniciar()

        elif not self.juegoActual.movidas:
            print("EMPATE")
            pygame.time.wait(2000)
            self._reiniciar()

    def _reiniciar(self):
        movidas = [(x, y, z)
                   for x in range(1, 5)
                   for y in range(1, 5)
                   for z in range(1, 5)]

        self.juegoActual = ElEstado('X', 0, {}, movidas)

    def run(self):
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.vis._handle_event(ev)

            self.vis.actualizar(self.juegoActual)

            if self.juegoActual.movidas and self.juegoActual.get_utilidad == 0:
                self.evolucionar()

            self.vis.clock.tick(60)


# ─── MAIN ─────────────────────────

def main():

    tablero = TableroVisual(4)

    humano = HumanoVisual(4, tablero.vis)
    ia = AgenteTresEnRaya(4)

    ia.altura = 2  # 🔥 importante (no pongas 3)

    tablero.insertar_humano(humano)
    tablero.insertar_ia(ia)

    tablero.run()


if __name__ == "__main__":
    main()