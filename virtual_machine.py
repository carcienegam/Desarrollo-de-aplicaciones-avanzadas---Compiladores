from quads import Quadruple
from semantics import FuncDirectory

class MemorySegment:
    # Memoria simple, guarda diccionario direccion -> valor
    def __init__(self):
        self.memory = {}

    def get(self, address):
        return self.memory.get(address, None)

    def set(self, address, value):
        self.memory[address] = value


class MemoryFrame:
    # Frame de ejecucion de funcion, guarda variables locales y temporales
    def __init__(self, func_name):
        self.func_name = func_name
        self.local = MemorySegment()
        self.temp = MemorySegment()


class VirtualMachine:
    def __init__(self, cuadruplos, dir_funcs, constant_table):
        self.cuadruplos = cuadruplos
        self.dir_funcs = dir_funcs
        self.const_mem = constant_table

        # Memoria global (1000-3999)
        self.global_mem = MemorySegment()

        # Frame actual (main / global) y nombre de función actual
        self.current_frame = MemoryFrame("global")
        self.current_func_name = "global"

        # Pila de llamadas
        self.call_stack = []

        # Frame preparado por ERA (antes de GOSUB)
        self.next_frame = None

        # Instruction pointer: indice de cuadruplo actual
        self.ip = 0

    def read(self, addr_or_name):
        # Lee el valor y determina que segmento  usar segun rango de dir
        if isinstance(addr_or_name, str):
            func_info = self.dir_funcs.get_funcs(addr_or_name)
            if func_info is None or func_info.return_address is None:
                raise RuntimeError(f"Intento de leer valor de retorno de '{addr_or_name}' sin return_address")
            address = func_info.return_address
        else:
            address = addr_or_name


        if address is None:
            return None

        # Constantes
        if address in self.const_mem:
            return self.const_mem[address]

        # Globales
        if 1000 <= address < 4000:
            return self.global_mem.get(address)

        # Locales
        if 4000 <= address < 7000:
            return self.current_frame.local.get(address)

        # Temporales
        if 7000 <= address < 10000:
            return self.current_frame.temp.get(address)

        raise RuntimeError(f"Invalid address: {address}")

    def write(self, address, value):
        # Escribe un valor en la dirección dada (global/local/temp)
        if 1000 <= address < 4000:
            self.global_mem.set(address, value)
        elif 4000 <= address < 7000:
            self.current_frame.local.set(address, value)
        elif 7000 <= address < 10000:
            self.current_frame.temp.set(address, value)
        else:
            raise RuntimeError(f"Invalid address: {address}")


    def run(self):
        # Ejecuto todos los cuadruplos hasta llegar al END
        while self.ip < len(self.cuadruplos):
            q = self.cuadruplos[self.ip]
            op, left, right, res = q.op, q.left_op, q.right_op, q.result


            if op == '=':
                self.write(res, self.read(left))

            elif op == '+':
                self.write(res, self.read(left) + self.read(right))

            elif op == '-':
                self.write(res, self.read(left) - self.read(right))

            elif op == '*':
                self.write(res, self.read(left) * self.read(right))

            elif op == '/':
                self.write(res, self.read(left) / self.read(right))

            elif op == '<':
                self.write(res, self.read(left) < self.read(right))

            elif op == '>':
                self.write(res, self.read(left) > self.read(right))

            elif op == '==':
                self.write(res, self.read(left) == self.read(right))

            elif op == '!=':
                self.write(res, self.read(left) != self.read(right))

            elif op == 'uminus':
                self.write(res, -self.read(left))

            # ------------------ Saltos ------------------
            elif op == 'GOTO':
                self.ip = res
                continue

            elif op == 'GOTOF':
                cond = self.read(left)
                if not cond:
                    self.ip = res
                    continue

            # ------------------ Print ------------------
            elif op == 'IMPRIME':
                # Dirección en result
                value = self.read(res)
                # Mas de 1 print en misma linea
                print(value, end='')

            # ------------------ Funciones ------------------
            elif op == 'ERA':
                # Crea un "frame" para la funcion y los parametros estaran dentro de este frame
                func_name = res
                self.next_frame = MemoryFrame(func_name)

            elif op == 'PARAM':
                # Mapea los parametros de la funcion con el directorio de funciones
                if self.next_frame is None:
                    raise RuntimeError("PARAM sin un ERA previo")

                value = self.read(left)
                param_tag = res  # "P1", "P2", ...
                idx = int(param_tag[1:]) - 1

                func_info = self.dir_funcs.get_funcs(self.next_frame.func_name)
                param_name = func_info.param_names[idx]
                param_info = func_info.var_table.table[param_name]
                param_addr = param_info.address

                self.next_frame.local.set(param_addr, value)

            elif op == 'GOSUB':
                # Se acaba la funcion
                func_name = res
                func_info = self.dir_funcs.get_funcs(func_name)
                if func_info is None or func_info.start_quad is None:
                    raise RuntimeError(f"GOSUB a función '{func_name}' sin start_quad")

                # Guardar estado actual en la pila de llamadas
                self.call_stack.append((self.current_frame, self.current_func_name, self.ip + 1))

                # Activar nuevo frame
                if self.next_frame is None:
                    raise RuntimeError("GOSUB sin ERA previo")
                self.current_frame = self.next_frame
                self.current_func_name = func_name
                self.next_frame = None

                # Saltar al primer cuadruplo de la función
                self.ip = func_info.start_quad
                continue

            elif op == 'RETURN':
                # Maneja el return, su valor con su direccion de retorno
                func_info = self.dir_funcs.get_funcs(self.current_func_name)
                if func_info.return_address is None:
                    raise RuntimeError(f"RETURN en función '{self.current_func_name}' sin return_address")

                value = self.read(res)
                self.write(func_info.return_address, value)

            elif op == 'ENDFUNC':
                # Se termina la funcion
                if not self.call_stack:
                    # Podría ser ENDFUNC sin llamada (no debería pasar)
                    return

                self.current_frame, self.current_func_name, ret_ip = self.call_stack.pop()
                self.ip = ret_ip
                continue

            # ------------------ END del programa ------------------
            elif op == 'END':
                print()
                return

            else:
                raise RuntimeError(f"Operación de cuádruplo no soportada: {op}")

            self.ip += 1
