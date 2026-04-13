from AgenteTresEnRaya import AgenteTresEnRaya
from Tablero import Tablero
from genetico import algoritmo_genetico

if __name__ == "__main__":

    print("\n==============================")
    print(" ENTRENANDO IA (GENÉTICO) ")
    print("==============================\n")

    # 🔥 ENTRENAMIENTO
    mejores_pesos = algoritmo_genetico()

    print("\n==============================")
    print(" PESOS FINALES OBTENIDOS ")
    print("==============================")
    print(mejores_pesos)
    print("==============================\n")

    # 🔴 IMPORTANTE: pausa para que puedas ver los pesos
    input("Presiona ENTER para iniciar el juego...")

    print("\n==============================")
    print(" INICIANDO PARTIDA IA vs IA ")
    print("==============================\n")

    # Crear agentes
    ia1 = AgenteTresEnRaya(4)
    ia2 = AgenteTresEnRaya(4)

    # 🔥 usar pesos aprendidos
    ia1.pesos = mejores_pesos
    ia2.pesos = mejores_pesos

    # 🔥 profundidad (no muy alta)
    ia1.altura = 2
    ia2.altura = 2

    tablero = Tablero(4)

    # Insertar jugadores
    tablero.insertar(ia1)
    tablero.insertar(ia2)

    # Ejecutar juego
    tablero.run()
    