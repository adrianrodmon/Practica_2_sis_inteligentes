from AgenteTresEnRaya import AgenteTresEnRaya


class HumanoTresEnRaya(AgenteTresEnRaya):
    def __init__(self, n=3):
        AgenteTresEnRaya.__init__(self, n)
        self.h = n
        self.v = n
        self.k = n

    def programa(self):
        print("Jugadas permitidas: {}".format(self.jugadas(self.estado)))
        print("")
        cad_movida = input('jugada? ejemplo (1,2,3): ')
        movida = eval(cad_movida)
        self.set_acciones(movida)