class SemanticError(Exception):
    """Errores semánticos (redeclaraciones, tipos inválidos, etc.)."""
    pass


# ----- Memoria virtual -----
class VirtualMemory:
    def __init__(self):
        self.memory = {
            'global': {'entero': 1000, 'flotante': 2000, 'bool': 3000},
            'local': {'entero': 4000, 'flotante': 5000, 'bool': 6000},
            'temporal': {'entero': 7000, 'flotante': 8000, 'bool': 9000},
            'const': {'entero': 10000, 'flotante': 11000, 'letrero': 12000}
        }

        self.counters = {
            segment: {t: memory for t, memory in tipos.items()}
            for segment, tipos in self.memory.items()
        }

        self.const_tables = {
            'entero': {},
            'flotante': {},
            'letrero': {}
        }

    def scope_segment(self, scope_level):
        return 'global' if scope_level == 'global' else 'local'
        
    def allocate_variable(self, scope_level, var_type) -> int:
        segment = self.scope_segment(scope_level)
        if var_type not in self.counters[segment]:
            raise ValueError(f"Type '{var_type}' not supported in segment '{segment}'")
        address = self.counters[segment][var_type]
        self.counters[segment][var_type] += 1
        return address
        
    def allocate_temporal(self, temp_type) -> int:
        segment = 'temporal'
        if temp_type not in self.counters[segment]:
            raise ValueError(f"Type '{temp_type}' not supported in segment '{segment}'")
        address = self.counters[segment][temp_type]
        self.counters[segment][temp_type] += 1
        return address
        
    def get_constant(self, value, const_type) -> int:
        if const_type not in self.const_tables:
            raise ValueError(f"Constant type '{const_type}' not supported")
        table = self.const_tables[const_type]

        if value in table:
            return table[value]
            
        segment = 'const'
        address = self.counters[segment][const_type]
        self.counters[segment][const_type] += 1
        table[value] = address
        return address
        
vm = VirtualMemory()

# ----- Variables -----

class VariableInfo:
    def __init__(self, name, var_type, scope_level, kind='var', address=None):
        self.name = name
        self.type = var_type
        self.scope_level = scope_level
        self.kind = kind
        self.address = address

    def __repr__(self):
        return f"variableInfo(name={self.name}, type={self.type}, scope_level={self.scope_level})"
    
class VariableTable:
    def __init__(self, scope_name):
        self.scope_name = scope_name
        self.table = {}

    def add_variable(self, name, var_type, kind='var'):
        if name in self.table:
            raise SemanticError(f"Variable '{name}' already declared in scope '{self.scope_name}'")
        
        address = vm.allocate_variable(self.scope_name, var_type)
        self.table[name] = VariableInfo(name, var_type, self.scope_name, kind, address)

    def get_vars(self, name):
        return self.table.get(name, None)
    
    def __repr__(self):
        return f"VariableTable(scope_name={self.scope_name}, vars={list(self.table.values())})"

# ----- Funciones -----

class FunctionInfo:
    def __init__(self, name, return_type):
        self.name = name
        self.return_type = return_type
        self.param_names = []
        self.param_types = []
        self.var_table = VariableTable(name)
        self.start_quad = None

    def add_parameter(self, name, param_type):
        self.param_names.append(name)
        self.param_types.append(param_type)
        self.var_table.add_variable(name, param_type, kind='param')

    def __repr__(self):
        return f"FunctionInfo(name={self.name}, return_type={self.return_type}, params={list(zip(self.param_names, self.param_types))}, vars={self.var_table})"
    
class FuncDirectory:
    def __init__(self):
        self.functions = {}

    def add_function(self, name, return_type):
        if name in self.functions:
            raise SemanticError(f"Function '{name}' already declared")
        self.functions[name] = FunctionInfo(name, return_type)

        return self.functions[name]

    def get_funcs(self, name):
        return self.functions.get(name)
    
    def exists(self, name):
        return name in self.functions
    
    def __repr__(self):
        return f"FuncDirectory(functions={list(self.functions.values())})"
    
def tipo_to_str(tipo):
    if tipo is None:
        return None
    
    if isinstance(tipo, tuple):
        return tipo[0]
    
    return tipo


# ----- Print de directorio de funciones -----
def function_directory(dir_funcs: FuncDirectory):
    print("----- Directorio de funciones -----")

    for func_name, func_info in dir_funcs.functions.items():
        print(f"Función: {func_name}")
        print(f"  Tipo de retorno: {func_info.return_type}")
        if func_info.param_names:
            print("  Parámetros:")
            for name, tipo in zip(func_info.param_names, func_info.param_types):
                print(f"    - {name}: {tipo}")
        else:
            print("  Parámetros: Ninguno")

        print("  Variables:")
        if func_info.var_table.table:
            for var_name, var_info in func_info.var_table.table.items():
                print(f"    - {var_name}: {var_info.type} (kind: {var_info.kind})")
        else:
            print("    Ninguna")
    