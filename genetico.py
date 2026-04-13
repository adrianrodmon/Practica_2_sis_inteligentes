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

    a1.altura = 1
    a2.altura = 1

    t = Tablero(4)
    t.insertar(a1)
    t.insertar(a2)

    for _ in range(10):
        for a in t.get_agentes():
            a.estado = t.juegoActual
            accion = a.podaAlphaBeta_eval(a.estado)
            t.juegoActual = a.getResultado(t.juegoActual, accion)

            if t.juegoActual.get_utilidad != 0:
                return t.juegoActual.get_utilidad

    return 0


def evaluar(ind, pobl):
    rival = random.choice(pobl)
    resultado = jugar(ind.pesos, rival.pesos)

    if resultado == 1:
        ind.fitness = 1
    elif resultado == -1:
        ind.fitness = -1
    else:
        ind.fitness = 0


def algoritmo_genetico():
    poblacion = [Individuo() for _ in range(4)]

    for gen in range(2):
        print(f"\n=== GENERACIÓN {gen} ===")

        for ind in poblacion:
            evaluar(ind, poblacion)
            print("Pesos:", ind.pesos, "Fitness:", ind.fitness)

        nueva = []

        for _ in range(len(poblacion)):
            p1 = random.choice(poblacion)
            p2 = random.choice(poblacion)

            hijo = Individuo()
            hijo.pesos = [0] + [
                (p1.pesos[i] + p2.pesos[i]) // 2
                for i in range(1, 5)
            ]

            if random.random() < 0.2:
                idx = random.randint(1, 4)
                hijo.pesos[idx] += random.randint(-3, 3)

            nueva.append(hijo)

        poblacion = nueva

    # 🔥 ESTO ES LO QUE TE FALTABA
    mejor = max(poblacion, key=lambda x: x.fitness)

    print("\n==============================")
    print("🏆 MEJOR PESO ENCONTRADO:")
    print(mejor.pesos)
    print("==============================\n")

    return mejor.pesos