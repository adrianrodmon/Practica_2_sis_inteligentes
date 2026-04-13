from AgenteTresEnRaya import AgenteTresEnRaya
from Tablero import Tablero
from genetico import algoritmo_genetico

if __name__ == "__main__":

    print("=== ENTRENANDO IA (GENÉTICO) ===\n")

    # 🔥 ENTRENAMIENTO
    mejores_pesos = algoritmo_genetico()

    print("\n=== JUGANDO CON PESOS ENTRENADOS ===\n")

    # Crear agentes
    ia1 = AgenteTresEnRaya(4)
    ia2 = AgenteTresEnRaya(4)

    # 🔥 usar pesos aprendidos
    ia1.pesos = mejores_pesos
    ia2.pesos = mejores_pesos

    # 🔥 ahora sí más profundidad para jugar mejor
    ia1.altura = 2
    ia2.altura = 2

    tablero = Tablero(4)

    tablero.insertar(ia1)
    tablero.insertar(ia2)

    tablero.run()