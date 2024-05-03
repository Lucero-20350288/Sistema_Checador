class JobPosition:
    def __init__(self, title, position_id):
        self.title = title
        self.position_id = position_id
        

    def toDBCollection(self):
        return {
            'title': self.title,
            'position_id': self.position_id
            
            # Puedes agregar más atributos según sea necesario
        }
