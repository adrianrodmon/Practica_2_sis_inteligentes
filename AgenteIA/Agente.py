# *************************************************************
# * Clase: Agente                                             *
# * Autor: Victor Estevez                                     *
# * Version: v2023.03.29                                      *
# * Descripcion: Implementacion de agente, percibe de su      *
# *              entorno, mapea las percepciones y modifica   *
# *              su entorno para resolucion de problema       *
# *************************************************************


class Agente:
    def __init__(self):
        self.__acciones = None
        self.vive = True

    def set_acciones(self, accion):
        self.__acciones = accion

    def get_acciones(self):
        return self.__acciones

    def esta_habilitado(self):
        return self.vive