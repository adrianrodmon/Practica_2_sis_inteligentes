from AgenteIA.Entorno import Entorno
from AgenteJugador import ElEstado

class Tablero(Entorno):

    def __init__(self, n=4):
        super().__init__()

        movidas = [(x,y,z)
                   for x in range(1,n+1)
                   for y in range(1,n+1)
                   for z in range(1,n+1)]

        self.juegoActual = ElEstado('X', 0, {}, movidas)

    def get_percepciones(self, agente):
        agente.estado = self.juegoActual
        if agente.estado.movidas:
            agente.programa()

    def ejecutar(self, agente):
        self.juegoActual = agente.getResultado(self.juegoActual, agente.get_acciones())
        agente.mostrar(self.juegoActual)

        if self.juegoActual.get_utilidad != 0:
            print("GANÓ:", "X" if self.juegoActual.get_utilidad == 1 else "O")
            agente.vive = False