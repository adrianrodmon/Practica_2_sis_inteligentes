# ******************************************************************
# * Clase: Entorno                                                 *
# * Autor: Victor Estevez                                          *
# * Version: v2023.03.29                                           *
# * Descripcion: Implementacion del entorno, proporciona           *
# *              percepciones a los agentes y ejecuta las acciones *
# *              de cada agente  que se encuentra en el            *
# ******************************************************************


class Entorno:

    def __init__(self):
        self.__agentes = []

    def get_percepciones(self, agente):
        raise Exception("No implementado")

    def ejecutar(self, agente):
        raise Exception("No implementado")

    def get_agentes(self):
        return self.__agentes

    def insertar(self, agente):
        self.__agentes.append(agente)

    def finalizar(self):
        return any(not a.esta_habilitado() for a in self.__agentes)

    def evolucionar(self):
        for agente in self.__agentes:
            self.get_percepciones(agente)
            self.ejecutar(agente)

    def run(self):
        while not self.finalizar():
            self.evolucionar()