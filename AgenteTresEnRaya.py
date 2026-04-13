from AgenteJugador import AgenteJugador, ElEstado

class AgenteTresEnRaya(AgenteJugador):

    def __init__(self, n=4):
        super().__init__(altura=2)
        self.n = n
        self.k = n

        # pesos (serán optimizados)
        self.pesos = [0, 1, 11, 47, 182]

        self.lineas = self.generar_lineas()

    def jugadas(self, estado):
        return estado.movidas

    def getResultado(self, estado, m):
        if m not in estado.movidas:
            return estado

        tablero = estado.tablero.copy()
        tablero[m] = estado.jugador

        movidas = list(estado.movidas)
        movidas.remove(m)

        utilidad = self.computa_utilidad(tablero)

        return ElEstado(
            jugador=('O' if estado.jugador == 'X' else 'X'),
            get_utilidad=utilidad,
            tablero=tablero,
            movidas=movidas
        )

    def get_utilidad(self, estado, jugador):
        return estado.get_utilidad if jugador == 'X' else -estado.get_utilidad

    def computa_utilidad(self, tablero):
        for linea in self.lineas:
            valores = [tablero.get(p) for p in linea]
            if valores.count('X') == self.k:
                return 1
            if valores.count('O') == self.k:
                return -1
        return 0

    def generar_lineas(self):
        n = self.n
        lineas = []

        for x in range(1, n+1):
            for y in range(1, n+1):
                lineas.append([(x,y,z) for z in range(1,n+1)])
                lineas.append([(x,z,y) for z in range(1,n+1)])
                lineas.append([(z,x,y) for z in range(1,n+1)])

        for z in range(1,n+1):
            lineas.append([(i,i,z) for i in range(1,n+1)])
            lineas.append([(i,n-i+1,z) for i in range(1,n+1)])

        lineas.append([(i,i,i) for i in range(1,n+1)])
        lineas.append([(i,i,n-i+1) for i in range(1,n+1)])

        return lineas

    def funcion_evaluacion(self, estado):

        if estado.get_utilidad == 1:
            return 100000
        if estado.get_utilidad == -1:
            return -100000

        score = 0
        tablero = estado.tablero

        for linea in self.lineas:
            valores = [tablero.get(p) for p in linea]

            if valores.count('X') > 0 and valores.count('O') > 0:
                continue

            x = valores.count('X')
            o = valores.count('O')

            if x > 0:
                score += self.pesos[x]
            elif o > 0:
                score -= self.pesos[o]

        # centro
        if tablero.get((2,2,2)) == 'X':
            score += 5
        elif tablero.get((2,2,2)) == 'O':
            score -= 5

        return score

    def mostrar(self, estado):
        for z in range(1, self.n+1):
            print(f"\nNivel {z}")
            for x in range(1, self.n+1):
                for y in range(1, self.n+1):
                    print(estado.tablero.get((x,y,z), '.'), end=" ")
                print()