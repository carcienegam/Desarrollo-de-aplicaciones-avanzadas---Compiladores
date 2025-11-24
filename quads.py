from semantics import vm

class EmptyStackError(Exception):
    pass

class Stack:
    def __init__(self, name="stack"):
        self.data = []
        self.name = name

    def push(self, value):
        self.data.append(value)

    def pop(self):
        if not self.data:
            raise EmptyStackError(f"Pop from empty stack '{self.name}'")
        return self.data.pop()
    
    def top(self):
        if not self.data:
            raise EmptyStackError(f"Top from empty stack '{self.name}'")
        return self.data[-1]
    
    def is_empty(self):
        return len(self.data) == 0
    
    def __len__(self):
        return len(self.data)
    
    def __repr__(self):
        return f"Stack(name={self.name}, data={self.data})"
    
class Quadruple:
    def __init__(self, op, left_op=None, right_op=None, result=None):
        self.op = op
        self.left_op = left_op
        self.right_op = right_op
        self.result = result

    def __repr__(self):
        return f"({self.op}, {self.left_op}, {self.right_op}, {self.result})"    
    

class QuadManager():
    def __init__(self):
        self.pila_operandos = Stack("pila_operandos")
        self.pila_operadores = Stack("pila_operadores")
        self.pila_tipos = Stack("pila_tipos")
        self.pila_saltos = Stack("pila_saltos")

        self.cuadruplos = [] # Lista de cuadruplos

        self.count_temporales = 0

    def new_temporal(self, tipo):
        name = f't{self.count_temporales}'
        self.count_temporales += 1
        address = vm.allocate_temporal(tipo)
        return address
        
    def add_cuadruplo(self, op, left_op=None, right_op=None, result=None):
        cuadruplo = Quadruple(op, left_op, right_op, result)
        self.cuadruplos.append(cuadruplo)
        return len(self.cuadruplos) - 1
    
    def get_cuadruplos(self, index):
        return self.cuadruplos[index]
    
    def fill_cuadruplos(self, index, result):
        self.cuadruplos[index].result = result

    def print_cuadruplos(self):
        print("----- Cuádruplos -----")
        for i, cuadruplo in enumerate(self.cuadruplos):
            print(f"{i}: {cuadruplo}")

    def __repr__(self):
        return (f"QuadManager(\n"
                f"  {self.pila_operandos}\n"
                f"  {self.pila_operadores}\n"
                f"  {self.pila_tipos}\n"
                f"  {self.pila_saltos}\n"
                f"  cuadruplos={self.cuadruplos}\n"
                f")")
    

# if __name__ == "__main__":
#     qm = QuadManager()
#     qm.pila_operandos.push("x")
#     qm.pila_operandos.push("y")
#     qm.pila_tipos.push("entero")
#     qm.pila_tipos.push("entero")
#     qm.pila_operadores.push("+")

#     t0 = qm.new_temporal()
#     qm.add_cuadruplo("+", "x", "y", t0)

#     qm.print_cuadruplos()
#     print(qm)
