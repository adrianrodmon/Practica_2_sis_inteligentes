from AgenteTresEnRaya import AgenteTresEnRaya
from Tablero import Tablero
from HumanoTresEnRaya import HumanoTresEnRaya

if __name__ == "__main__":

    # Tamaño del juego (IMPORTANTE: 4x4x4)
    N = 4

    # Crear agentes
    humano = HumanoTresEnRaya(N)
    ia = AgenteTresEnRaya(N)

    # Configuración IA
    ia.tecnica = "fun_eval"
    ia.altura = 3   # profundidad de búsqueda alpha-beta

    # Crear tablero
    tablero = Tablero(N)

    # Insertar jugadores (orden importa: X empieza)
    tablero.insertar(humano)   # X
    tablero.insertar(ia)       # O

    print("\n=== INICIANDO 3D TIC-TAC-TOE 4x4x4 ===\n")

    # Ejecutar juego
    tablero.run()