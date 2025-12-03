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

    def print_cuadruplos_symbolic(self, dir_funcs, vm):
        """
        Imprime los cuádruplos traduciendo direcciones virtuales a:
        - nombres de variables (x, y, foo.a)
        - literales de constantes (3, 1.5, "hola")
        - temporales (t0, t1, ...)
        Si el operando no es int, se imprime tal cual.
        """
        # 1) Direcciones de variables -> nombres
        addr_to_name = {}
        for func_name, func_info in dir_funcs.functions.items():
            for var_name, var_info in func_info.var_table.table.items():
                if func_name == "global":
                    pretty_name = var_name
                else:
                    pretty_name = f"{func_name}.{var_name}"
                addr_to_name[var_info.address] = pretty_name

        # 2) Direcciones de constantes -> literals
        addr_to_const = {}
        for tipo, table in vm.const_tables.items():
            for value, addr in table.items():
                if tipo == 'letrero':
                    addr_to_const[addr] = repr(value)  # "texto"
                else:
                    addr_to_const[addr] = str(value)

        # 3) Temporales (lo que no es ni var ni const)
        temp_map = {}
        temp_count = 0
        for q in self.cuadruplos:
            for op in (q.left_op, q.right_op, q.result):
                if isinstance(op, int) and op not in addr_to_name and op not in addr_to_const:
                    if op not in temp_map:
                        temp_map[op] = f"t{temp_count}"
                        temp_count += 1

        def fmt(op):
            if op is None:
                return "_"
            if not isinstance(op, int):
                return str(op)
            if op in addr_to_name:
                return addr_to_name[op]
            if op in addr_to_const:
                return addr_to_const[op]
            if op in temp_map:
                return temp_map[op]
            return f"@{op}"  # fallback: dirección cruda

        print("----- Cuádruplos (formato simbólico) -----")
        for i, q in enumerate(self.cuadruplos):
            # Si es un salto: NO formatear result como dirección
            if q.op in ["GOTO", "GOTOF", "GOTOT", "GOSUB"]:
                res = q.result  # índice de cuádruplo, NO dirección virtual
            else:
                res = fmt(q.result)

            print(f"{i}: ({q.op}, {fmt(q.left_op)}, {fmt(q.right_op)}, {res})")
        print("------------------------------------------")


        
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
