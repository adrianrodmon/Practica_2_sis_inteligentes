from AgenteIA.Agente import Agente
from collections import namedtuple
import time

ElEstado = namedtuple('ElEstado', 'jugador, get_utilidad, tablero, movidas')

class AgenteJugador(Agente):

    def __init__(self, altura=2):
        super().__init__()
        self.estado = None
        self.tecnica = "fun_eval"
        self.altura = altura

    def jugadas(self, estado):
        raise Exception("No implementado")

    def get_utilidad(self, estado, jugador):
        raise Exception("No implementado")

    def testTerminal(self, estado):
        return estado.get_utilidad != 0 or len(estado.movidas) == 0

    def getResultado(self, estado, m):
        raise Exception("No implementado")

    def funcion_evaluacion(self, estado):
        raise Exception("No implementado")

    def podaAlphaBeta_eval(self, estado):

        jugador = estado.jugador
        # funcion_evaluacion devuelve score desde perspectiva X
        # Si jugamos como O, invertir para que maximize correctamente
        factor = 1 if jugador == 'X' else -1

        def ordenar(e):
            """Ordena movidas: ganadoras, bloqueos, luego centro."""
            wins, blocks, rest = [], [], []
            opp = 'O' if e.jugador == 'X' else 'X'
            for m in self.jugadas(e):
                t = e.tablero.copy()
                t[m] = e.jugador
                if self.computa_utilidad(t) != 0:
                    wins.append(m)
                    continue
                t2 = e.tablero.copy()
                t2[m] = opp
                if self.computa_utilidad(t2) != 0:
                    blocks.append(m)
                    continue
                rest.append(m)
            c = (self.n + 1) / 2.0
            rest.sort(key=lambda m: sum((x - c) ** 2 for x in m))
            return wins + blocks + rest

        def max_value(e, alpha, beta, depth):
            if self.testTerminal(e):
                return self.get_utilidad(e, jugador)

            if depth == 0:
                return self.funcion_evaluacion(e) * factor

            v = -float('inf')
            for a in ordenar(e):
                v = max(v, min_value(self.getResultado(e, a), alpha, beta, depth - 1))
                if v >= beta:
                    return v
                alpha = max(alpha, v)
            return v

        def min_value(e, alpha, beta, depth):
            if self.testTerminal(e):
                return self.get_utilidad(e, jugador)

            if depth == 0:
                return self.funcion_evaluacion(e) * factor

            v = float('inf')
            for a in ordenar(e):
                v = min(v, max_value(self.getResultado(e, a), alpha, beta, depth - 1))
                if v <= alpha:
                    return v
                beta = min(beta, v)
            return v

        mejor_accion = None
        mejor_valor = -float('inf')

        for a in ordenar(estado):
            valor = min_value(self.getResultado(estado, a), -float('inf'), float('inf'), self.altura)
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_accion = a

        return mejor_accion

    def programa(self):
        print("IA pensando...")
        accion = self.podaAlphaBeta_eval(self.estado)
        self.set_acciones(accion)
        print("IA jugó:", accion)