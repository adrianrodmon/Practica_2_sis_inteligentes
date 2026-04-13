import random
from AgenteTresEnRaya import AgenteTresEnRaya
from Tablero import Tablero

class Individuo:
    def __init__(self):
        self.pesos = [0,
                      random.randint(1,5),
                      random.randint(5,15),
                      random.randint(15,50),
                      random.randint(50,200)]
        self.fitness = 0


def jugar(p1, p2):
    a1 = AgenteTresEnRaya(4)
    a2 = AgenteTresEnRaya(4)

    a1.pesos = p1
    a2.pesos = p2

    # 🔥 CLAVE: profundidad baja
    a1.altura = 1
    a2.altura = 1

    t = Tablero(4)
    t.insertar(a1)
    t.insertar(a2)

    for _ in range(10):  # 🔥 menos turnos
        for a in t.get_agentes():
            a.estado = t.juegoActual
            acc = a.podaAlphaBeta_eval(a.estado)
            t.juegoActual = a.getResultado(t.juegoActual, acc)

            if t.juegoActual.get_utilidad != 0:
                return t.juegoActual.get_utilidad

    return 0


def evaluar(ind, pobl):
    # 🔥 solo 1 partida (muy rápido)
    rival = random.choice(pobl)
    resultado = jugar(ind.pesos, rival.pesos)

    if resultado == 1:
        ind.fitness = 1
    else:
        ind.fitness = 0


def algoritmo_genetico():
    # 🔥 población pequeña
    pobl = [Individuo() for _ in range(4)]

    for gen in range(2):  # 🔥 pocas generaciones
        print("Generación", gen)

        for ind in pobl:
            evaluar(ind, pobl)

        nueva = []

        for _ in pobl:
            p1 = random.choice(pobl)
            p2 = random.choice(pobl)

            hijo = Individuo()
            hijo.pesos = [0] + [
                (p1.pesos[i] + p2.pesos[i]) // 2
                for i in range(1, 5)
            ]

            # 🔥 mutación leve
            if random.random() < 0.2:
                hijo.pesos[random.randint(1, 4)] += random.randint(-3, 3)

            nueva.append(hijo)

        pobl = nueva

    mejor = max(pobl, key=lambda x: x.fitness)

    print("\nMEJOR PESO ENCONTRADO:")
    print(mejor.pesos)

    return mejor.pesos