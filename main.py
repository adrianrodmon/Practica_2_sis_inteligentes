from AgenteTresEnRaya import AgenteTresEnRaya
from Tablero import Tablero
from genetico import algoritmo_genetico
import random


# 🔹 IA RANDOM
class AgenteRandom(AgenteTresEnRaya):

    def programa(self):
        accion = random.choice(self.estado.movidas)
        self.set_acciones(accion)


# 🔹 JUGAR PARTIDA SIN PRINT
def jugar_partida(a1, a2):

    tablero = Tablero(4)
    tablero.insertar(a1)
    tablero.insertar(a2)

    for _ in range(30):
        for a in tablero.get_agentes():
            a.estado = tablero.juegoActual
            accion = a.podaAlphaBeta_eval(a.estado)
            tablero.juegoActual = a.getResultado(tablero.juegoActual, accion)

            if tablero.juegoActual.get_utilidad != 0:
                return tablero.juegoActual.get_utilidad

    return 0


if __name__ == "__main__":

    print("\n=== ENTRENANDO IA (GENÉTICO) ===\n")

    mejores_pesos = algoritmo_genetico()

    print("\nPesos obtenidos:", mejores_pesos)

    # 🔴 CREAR AGENTES

    # IA con genético
    ia_gen = AgenteTresEnRaya(4)
    ia_gen.pesos = mejores_pesos
    ia_gen.altura = 2

    # IA normal
    ia_normal = AgenteTresEnRaya(4)
    ia_normal.altura = 2

    # IA random
    ia_random = AgenteRandom(4)

    # 🔥 COMPARACIONES

    print("\n=== COMPARACIÓN ===\n")

    partidas = 5

    # Genético vs Normal
    wins = 0
    for _ in range(partidas):
        res = jugar_partida(ia_gen, ia_normal)
        if res == 1:
            wins += 1

    print(f"Genético vs Normal → ganó {wins}/{partidas}")

    # Genético vs Random
    wins = 0
    for _ in range(partidas):
        res = jugar_partida(ia_gen, ia_random)
        if res == 1:
            wins += 1

    print(f"Genético vs Random → ganó {wins}/{partidas}")

    print("\n=== FIN ===")