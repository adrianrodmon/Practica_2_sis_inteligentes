from AgenteIA.Agente import Agente
from collections import namedtuple

ElEstado = namedtuple('ElEstado', 'jugador, get_utilidad, tablero, movidas')

class AgenteJugador(Agente):

    def __init__(self, altura=2):
        super().__init__()
        self.estado = None
        self.altura = altura

    def jugadas(self, estado):
        raise Exception("No implementado")

    def get_utilidad(self, estado, jugador):
        raise Exception("No implementado")

    def getResultado(self, estado, m):
        raise Exception("No implementado")

    def testTerminal(self, estado):
        return estado.get_utilidad != 0 or len(estado.movidas) == 0

    def funcion_evaluacion(self, estado):
        raise Exception("No implementado")

    def podaAlphaBeta_eval(self, estado):

        jugador = estado.jugador

        def max_value(e, alpha, beta, depth):
            if self.testTerminal(e):
                return self.get_utilidad(e, jugador)
            if depth == 0:
                return self.funcion_evaluacion(e)

            v = -float('inf')
            for a in self.jugadas(e):
                v = max(v, min_value(self.getResultado(e, a), alpha, beta, depth-1))
                if v >= beta:
                    return v
                alpha = max(alpha, v)
            return v

        def min_value(e, alpha, beta, depth):
            if self.testTerminal(e):
                return self.get_utilidad(e, jugador)
            if depth == 0:
                return self.funcion_evaluacion(e)

            v = float('inf')
            for a in self.jugadas(e):
                v = min(v, max_value(self.getResultado(e, a), alpha, beta, depth-1))
                if v <= alpha:
                    return v
                beta = min(beta, v)
            return v

        mejor = None
        mejor_val = -float('inf')

        for a in self.jugadas(estado):
            v = min_value(self.getResultado(estado, a), -float('inf'), float('inf'), self.altura)
            if v > mejor_val:
                mejor_val = v
                mejor = a

        return mejor

    def programa(self):
        accion = self.podaAlphaBeta_eval(self.estado)
        self.set_acciones(accion)