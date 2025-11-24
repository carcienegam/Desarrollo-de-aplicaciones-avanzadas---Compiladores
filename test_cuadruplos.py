# test_quads_patito.py

import importlib
from semantics import SemanticError

tests = [
    (
        "Asignacion simple",
        """
        programa p;
        vars
            x : entero;
        inicio {
            x = 3 + 5;
        }
        fin
        """
    ),
    (
        "Con parentesis",
        """
        programa p;
        vars
            x, y : entero;
        inicio {
            x = 3 + 4 * 2;
            y = (3 + 4) * 2;
        }
        fin
        """
    ),
    (
        "Esribe",
        """
        programa p;
        vars
            x : entero;
        inicio {
            x = 10;
            escribe("Valor de x: ", x, " doble: ", x * 2);
        }
        fin
        """
    ),
    (
        "Funcion y llamada simple",
        """
        programa p;
        vars
            x, y : entero;
        entero suma(a : entero, b : entero) {
            {
                escribe(a + b);
            }
        };
        inicio {
            x = 3;
            y = 4;
            suma(x, y);
        }
        fin
        """
    ),
    (
        "Expresion relacion (si haz)",
        """
        programa p;
        vars
            x : entero;
        inicio {
            x = 5;
            si (x > 3) haz {
                escribe("mayor que 3");
            };
        }
        fin
        """
    ),
]


def tests_cuadrupos(name: str, code: str):
    print(f"\n----------")
    print(f"Test: {name}")
    print("----------")

    import parser_patito
    importlib.reload(parser_patito)

    parser = parser_patito.parser
    lexer = parser_patito.lexer
    quad_manager = parser_patito.quad_manager

    try:
        result = parser.parse(code, lexer=lexer)
        print("AST:")
        print(result)

        print("\nDIRECTORIO DE FUNCIONES:")
        from semantics import function_directory
        function_directory(parser_patito.dir_funcs)

        print("\nCUÁDUPLOS GENERADOS:")
        quad_manager.print_cuadruplos()

    except SemanticError as e:
        print("Error semántico:", e)


def run_all():
    for name, code in tests:
        tests_cuadrupos(name, code)


if __name__ == "__main__":
    run_all()
