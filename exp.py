class EstadoCartas:
    def __init__(self, cartas_jugador, cartas_oponente, puntos_jugador=0, puntos_oponente=0):
        self.cartas_jugador = cartas_jugador
        self.cartas_oponente = cartas_oponente
        self.puntos_jugador = puntos_jugador
        self.puntos_oponente = puntos_oponente

    def es_terminal(self):
        # El juego termina cuando ambos jugadores no tienen más cartas.
        return len(self.cartas_jugador) == 0 and len(self.cartas_oponente) == 0

    def utilidad(self):
        # Retorna la diferencia en puntos.
        return self.puntos_jugador - self.puntos_oponente


class AgenteCartasExpectiminimax:

    def __init__(self, max_profundidad=3):
        self.max_profundidad = max_profundidad

    def jugada_expectiminimax(self, estado):
        mejor_valor = -float('inf')
        mejor_movida = None

        for carta in estado.cartas_jugador:
            nuevo_estado = self.getResultado(estado, carta, es_turno_jugador=True)
            valor = self.expectiminimax(nuevo_estado, 0, es_turno_jugador=False)
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_movida = carta

        return mejor_movida

    def expectiminimax(self, estado, profundidad, es_turno_jugador):
        if estado.es_terminal() or profundidad == self.max_profundidad:
            return estado.utilidad()

        if es_turno_jugador:  # Nodo de Maximización
            max_valor = -float('inf')
            for carta in estado.cartas_jugador:
                nuevo_estado = self.getResultado(estado, carta, es_turno_jugador=True)
                valor = self.expectiminimax(nuevo_estado, profundidad + 1, es_turno_jugador=False)
                max_valor = max(max_valor, valor)
            return max_valor

        else:  # Nodo de Minimización (oponente)
            min_valor = float('inf')
            for carta in estado.cartas_oponente:
                nuevo_estado = self.getResultado(estado, carta, es_turno_jugador=False)
                valor = self.expectiminimax(nuevo_estado, profundidad + 1, es_turno_jugador=True)
                min_valor = min(min_valor, valor)
            return min_valor

    def getResultado(self, estado, carta_jugada, es_turno_jugador):
        """
        Genera el nuevo estado tras jugar una carta.
        """
        # El oponente también juega una carta en su turno.
        if es_turno_jugador:
            cartas_oponente = estado.cartas_oponente.copy()
            carta_oponente = random.choice(cartas_oponente)
            cartas_oponente.remove(carta_oponente)

            # Verifica quién gana la ronda.
            if carta_jugada > carta_oponente:
                nuevo_puntos_jugador = estado.puntos_jugador + 1
                nuevo_puntos_oponente = estado.puntos_oponente
            else:
                nuevo_puntos_jugador = estado.puntos_jugador
                nuevo_puntos_oponente = estado.puntos_oponente + 1

            cartas_jugador = estado.cartas_jugador.copy()
            cartas_jugador.remove(carta_jugada)

            return EstadoCartas(cartas_jugador, cartas_oponente, nuevo_puntos_jugador, nuevo_puntos_oponente)

        else:  # Turno del oponente
            cartas_jugador = estado.cartas_jugador.copy()
            carta_jugador = random.choice(cartas_jugador)
            cartas_jugador.remove(carta_jugador)

            # Verifica quién gana la ronda.
            if carta_jugador > carta_jugada:
                nuevo_puntos_jugador = estado.puntos_jugador + 1
                nuevo_puntos_oponente = estado.puntos_oponente
            else:
                nuevo_puntos_jugador = estado.puntos_jugador
                nuevo_puntos_oponente = estado.puntos_oponente + 1

            cartas_oponente = estado.cartas_oponente.copy()
            cartas_oponente.remove(carta_jugada)

            return EstadoCartas(cartas_jugador, cartas_oponente, nuevo_puntos_jugador, nuevo_puntos_oponente)

    # Aquí puedes agregar una función de evaluación si quieres limitar la búsqueda