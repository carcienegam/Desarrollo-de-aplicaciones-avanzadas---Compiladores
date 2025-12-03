import importlib
from semantics import SemanticError

# ============================================================
# LISTA DE TESTS
# ============================================================

tests = [
    # ---------------------------------------------------------------------
    # 1. ARITMÉTICA Y ASIGNACIÓN
    # ---------------------------------------------------------------------
    (
        "T1: Asignación y Expresión con Paréntesis",
        """
        programa T1_Asignacion;
        vars
            x : int;
            y : int;
        start {
            // Test 1: Operaciones simples (3 + 4 * 2 = 11)
            x = 3 + 4 * 2;
            // Test 2: Precedencia con paréntesis ((3 + 4) * 2 = 14)
            y = (3 + 4) * 2;
            print("x:", x, "y:", y);
        }
        end
        """
    ),

    (
        "T2: Operaciones Float y Unario",
        """
        programa T2_FloatUnario;
        vars
            f1 : float;
            f2 : float;
        start {
            // Test 1: Float y division
            f1 = 10.0 / 4.0 + 1.5; // 2.5 + 1.5 = 4.0
            // Test 2: Unary Minus
            f2 = -10.0;
            f1 = f1 + f2; // 4.0 + (-10.0) = -6.0
            print("f1:", f1);
        }
        end
        """
    ),

    # ---------------------------------------------------------------------
    # 2. FUNCIONES (ERA, PARAM, GOSUB, RETURN)
    # ---------------------------------------------------------------------
    (
        "T3: Función con Retorno y Parámetros",
        """
        programa T3_FuncRetorno;
        vars
            res : int;
            val : int;

        int sumaDoble(a : int, b : int) {
            {
                return (a + b) * 2;
            }
        };

        start {
            val = 5;
            // Llamada: sumaDoble(5, 3) = 16
            res = sumaDoble(val, 3);
            print("Respuesta T3 (16): ", res);
        }
        end
        """
    ),

    (
        "T4: Función Nula y Llamada como Estatuto",
        """
        programa T4_FuncNula;
        vars
            x : int;

        nula mensaje(s : int) {
            {
                print("Llamada a nula, x es: ", s);
            }
        };

        start {
            x = 100;
            mensaje(x);
        }
        end
        """
    ),

    # ---------------------------------------------------------------------
    # 3. ESTRUCTURAS DE CONTROL
    # ---------------------------------------------------------------------
    (
        "T5: Condicional IF-ELSE",
        """
        programa T5_IfElse;
        vars
            a : int;
            res : int;
        start {
            a = 15;

            if (a > 10) {
                res = 1;
            }
            else {
                res = 0;
            };
            print("Resultado T5.1 (1): ", res);

            if (a != 15) {
                res = 2;
            }
            else {
                res = 3;
            };
            print("Resultado T5.2 (3): ", res);
        }
        end
        """
    ),

    (
        "T6: Ciclo WHILE / DO-WHILE",
        """
        programa T6_While;
        vars
            i : int;
            suma : int;
        start {
            i = 0;
            suma = 0;

            while (i < 4) do {
                suma = suma + i;
                i = i + 1;
            }
            

            print("Suma T6 (6): ", suma);
        }
        end
        """
    ),

    # ---------------------------------------------------------------------
    # 4. ALCANCE, ANIDACIÓN, COMPLEJIDAD
    # ---------------------------------------------------------------------
    (
        "T7: Variables Globales y Locales",
        """
        programa T7_Alcance;
        vars
            global_val : int;

        int calcular(a : int) {
            vars
                local_val : int;
            {
                local_val = a * 10;
                global_val = global_val + 1;
                return local_val + global_val;
            }
        };

        start {
            global_val = 100;
            global_val = calcular(5);
            print("Global Final T7 (151): ", global_val);
        }
        end
        """
    ),

    (
        "T8: Condicional Anidado",
        """
        programa T8_Anidado;
        vars
            x : int;
            y : int;
        start {
            x = 2;
            y = 10;

            if (x < y) {
                if (y == (5 * x)) {
                    print("Test Anidado 1: OK");
                }
                else {
                    print("Test Anidado 1: FALLO");
                };
            }
            else {
                print("Test Anidado 2: FALLO");
            };
        }
        end
        """
    ),
]


# ============================================================
# FUNCIÓN PARA CORRER UN TEST
# ============================================================

def tests_cuadrupos(name: str, code: str):
    print(f"\n===============================")
    print(f"Test: {name}")
    print("===============================")

    # Recargar el parser y sus estados
    import parser_patito
    importlib.reload(parser_patito)

    parser = parser_patito.parser
    lexer = parser_patito.lexer
    quad_manager = parser_patito.quad_manager
    dir_funcs = parser_patito.dir_funcs
    vm = parser_patito.vm

    try:
        parser.parse(code, lexer=lexer)
        print("✔ AST generado correctamente.")

        # Directorio de funciones
        print("\nDIRECTORIO DE FUNCIONES:")
        from semantics import function_directory
        function_directory(dir_funcs)

        # Cuádruplos
        print("\nCUÁDUPLOS GENERADOS:")
        quad_manager.print_cuadruplos_symbolic(dir_funcs, vm)

    except SemanticError as e:
        print("❌ Error semántico:", e)
    except Exception as e:
        print("❌ Error inesperado:", e)


# ============================================================
# CORRER TODOS LOS TESTS
# ============================================================

def run_all():
    for name, code in tests:
        tests_cuadrupos(name, code)


if __name__ == "__main__":
    run_all()
