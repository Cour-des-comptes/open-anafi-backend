class Var:
    LIST_TYPE_APPEL = ['SX', 'SS', 'BR', 'BO', 'NB', 'BE', 'BX']

    def __init__(self, name, type_solde, minus):
        self.name = name
        self.type_solde = type_solde
        self.minus = minus
    def __repr__(self):
        return f'{self.name} : {self.type_solde}'
    
class Indic:
    def __init__(self, name, offset, minus):
        self.name = name
        self.offset = offset
        self.minus = minus
    def __repr__(self):
        return f'{self.name} : {self.offset}'