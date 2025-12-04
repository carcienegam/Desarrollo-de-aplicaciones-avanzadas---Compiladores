from parser_patito import parser, lexer, quad_manager, dir_funcs
from semantics import vm
from virtual_machine import VirtualMachine


# ===========================================================
#  Helpers
# ===========================================================

def make_const_table(vm):
    """Convierte vm.const_tables (value->addr) en addr->value."""
    const_addr_to_value = {}
    for tipo, table in vm.const_tables.items():
        for value, addr in table.items():
            const_addr_to_value[addr] = value
    return const_addr_to_value


def run_patito_program(name, code):
    print("\n" + "="*60)
    print(f"TEST: {name}")
    print("="*60)

    # Reset global state
    quad_manager.cuadruplos.clear()
    quad_manager.pila_operandos.data.clear()
    quad_manager.pila_tipos.data.clear()
    quad_manager.pila_operadores.data.clear()
    quad_manager.pila_saltos.data.clear()

    dir_funcs.functions.clear()
    dir_funcs.add_function("global", "nula")
    vm.reset_temporals()
    vm.counters['global'] = {'int':0,'float':0,'bool':0}
    vm.counters['local'] = {'int':0,'float':0,'bool':0}
    vm.counters['temporal'] = {'int':0,'float':0,'bool':0}
    vm.counters['const'] = {'int':0,'float':0,'letrero':0}
    vm.const_tables = {'int':{},'float':{},'letrero':{}}

    # Parsear
    try:
        parser.parse(code, lexer=lexer)
    except Exception as e:
        print("❌ ERROR durante el parseo:", e)
        return

    # Preparar constantes
    const_addr_to_value = make_const_table(vm)

    # Ejecutar VM
    try:
        vmachine = VirtualMachine(quad_manager.cuadruplos, dir_funcs, const_addr_to_value)
        vmachine.run()
    except Exception as e:
        print("❌ ERROR durante ejecución de la VM:", e)
        return

    print("\n✔ TEST FINALIZADO")



# ===========================================================
#  TEST CASES
# ===========================================================

TESTS = [
    (
        "Factorial en MAIN (iterativo)",
        """
        programa T;
        vars
            n : int;
            fact : int;

        main {
            n = 5;
            fact = 1;

            while (n > 1) do {
                fact = fact * n;
                n = n - 1;
            };

            print("Fact main: ", fact);
        }
        end
        """
    ),

    (
        "Factorial en función iterativa",
        """
        programa T;
        vars
            n : int;
            r : int;

        int factorial(k:int) {
            vars
                f:int;
            {
                f = 1;
                while (k > 1) do {
                    f = f * k;
                    k = k - 1;
                };
                return f;
            }
        };

        main {
            n = 5;
            r = factorial(n);
            print("Fact iter: ", r);
        }
        end
        """
    ),

    (
        "Factorial recursivo",
        """
        programa T;
        vars
            n : int;
            r : int;

        int fact(x:int) {
            {
                if (x == 0) {
                    return 1;
                }
                else {
                    return x * fact(x - 1);
                };
            }
        };

        main {
            n = 5;
            r = fact(n);
            print("Fact rec: ", r);
        }
        end
        """
    ),

    (
        "Fibonacci en MAIN (iterativo)",
        """
        programa T;
        vars
            n : int;
            a : int;
            b : int;
            t : int;

        main {
            n = 6;
            a = 0;
            b = 1;

            while (n > 0) do {
                print(a, " ");
                t = a + b;
                a = b;
                b = t;
                n = n - 1;
            };

            print("FIN");
        }
        end
        """
    ),

    (
        "Fibonacci iterativo en función",
        """
        programa T;
        vars
            r : int;

        int fib(k:int) {
            vars
                a:int;
                b:int;
                t:int;
            {
                if (k == 0) {
                    return 0;
                };
                if (k == 1) {
                    return 1;
                };

                a = 0;
                b = 1;

                while (k > 1) do {
                    t = a + b;
                    a = b;
                    b = t;
                    k = k - 1;
                };

                return b;
            }
        };

        main {
            r = fib(6);
            print("Fib iter: ", r);
        }
        end
        """
    ),

    (
        "Fibonacci recursivo",
        """
        programa T;
        vars
           n, resultado: int;

        int fibonacci(x: int) {
            vars a, b: int;
            {
                if (x < 2) {
                    return(x);
                } else {
                    return(fibonacci(x - 1) + fibonacci(x - 2));
                };
            }
        };

        main {
            n = 20;
            resultado = fibonacci(n);
            print("Fibonacci de ", n, " es: ", resultado);
        }
        end
        """
    ),

    (
        "Control de flujo general (if + while)",
        """
        programa T;
        vars
            x : int;
            y : int;

        main {
            x = 0;
            y = 3;

            while (y > 0) do {
                if (x == 0) {
                    print("cero ");
                }
                else {
                    print("nz ");
                };

                x = x + 1;
                y = y - 1;
            };

            print("fin");
        }
        end
        """
    ),

    (
        "Ejemplo de clase",
        """
        programa x;
        vars
            i : int;
            j : int;

        nula uno(a:int) {
            {
                i = a * 2;
                if (i < a + 4) {
                    uno(a + 1);
                };
                print(i);
            }
        };

        int dos(b:int) {
            {
                b = b * i + j;
                return (b * 2);
            }
        };

        main {
            i = 2;
            j = i * 2 - 1;
            uno(j);
            print(i + dos(i + j));
        }
        end
        """
    ),
]


# ===========================================================
#  EJECUTAR TODOS LOS TESTS
# ===========================================================
if __name__ == "__main__":
    for name, code in TESTS:
        run_patito_program(name, code)

