class Incidencia:
    def __init__(self, descripcion):
      self.incidencias = descripcion

    def toDB(self):
        return {
            'incidencia': self.incidencias,
        }