class Stack:
    def __init__(self):
        self.items = []

    def push(self, item): #Insertar a la cima
        self.items.append(item)

    def pop(self): #Eliminar y devolver la cima
        if not self.is_empty():
            return self.items.pop()
        return None

    def peek(self): #Devolver la cima sin eliminar
        if not self.is_empty():
            return self.items[-1]
        return None

    def is_empty(self): #Indica si esta vacia
        return len(self.items) == 0

    def size(self): #Indica size de un stack
        return len(self.items)

    def __str__(self): #Representación para devolver
        return str(self.items)