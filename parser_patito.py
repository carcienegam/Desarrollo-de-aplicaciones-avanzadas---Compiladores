import ply.yacc as yacc
from lex_patito import tokens, build_lexer

from semantics import FuncDirectory, SemanticError, tipo_to_str, function_directory
from semantic_cube import check_types

from quads import QuadManager

lexer = build_lexer()

precedence = (
    ('left', 'GREATERTHAN', 'LESSTHAN', 'EQUAL', 'NOTEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIVIDE'),
)

start = 'programa'

dir_funcs = FuncDirectory()

current_function = None
dir_funcs.add_function("global", "nula")

quad_manager = QuadManager()

# ----- Helper Functions -----
def get_var_type(name):
    if current_function and dir_funcs.exists(current_function):
        t = dir_funcs.get_funcs(current_function).var_table.get_vars(name)
        if t:
            return t.type

    g = dir_funcs.get_funcs("global").var_table.get_vars(name)
    if g:
        return g.type

    raise SemanticError(f"Variable '{name}' not declared")

def binop_cuadruplo(op):
    # Cuadruplos para operaciones binarias (+, -, *, /)
    right = quad_manager.pila_operandos.pop()
    right_type = quad_manager.pila_tipos.pop()
    left = quad_manager.pila_operandos.pop()
    left_type = quad_manager.pila_tipos.pop()

    result_type = check_types(op, left_type, right_type)
    temporal = quad_manager.new_temporal()
    quad_manager.add_cuadruplo(op, left, right, temporal)

    quad_manager.pila_operandos.push(temporal)
    quad_manager.pila_tipos.push(result_type)

    return ('temp', temporal, result_type)

def relop_cuadruplo(op):
    # Cuadruplos para operaciones relacionales (<, >, ==, !=)
    right = quad_manager.pila_operandos.pop()
    right_type = quad_manager.pila_tipos.pop()
    left = quad_manager.pila_operandos.pop()
    left_type = quad_manager.pila_tipos.pop()

    result_type = check_types(op, left_type, right_type)
    temporal = quad_manager.new_temporal()
    quad_manager.add_cuadruplo(op, left, right, temporal)

    quad_manager.pila_operandos.push(temporal)
    quad_manager.pila_tipos.push(result_type)

    return ('temp', temporal, result_type)

def unminus_cuadruplo(op):
    # Cuadruplos para operación unaria (-)
    operand = quad_manager.pila_operandos.pop()
    operand_type = quad_manager.pila_tipos.pop()

    temporal = quad_manager.new_temporal()
    quad_manager.add_cuadruplo('uminus', operand, None, temporal)

    quad_manager.pila_operandos.push(temporal)
    quad_manager.pila_tipos.push(operand_type)

    return ('temp', temporal, operand_type)


# ----- 1. Programa -----
def p_programa(p):
    '''programa : PROGRAMA ID SEMICOLON skipVars cycleFuncs INICIO CUERPO FIN'''
    p[0] = ('programa', p[2], p[4], p[5], p[7])

def p_skipVars(p):
    '''skipVars :
                  | VARS_sect '''
    if len(p) == 1:
        p[0] = None
    else:
        vars_ast = p[1]
        tag, decls = vars_ast

        if current_function and dir_funcs.exists(current_function):
            func_info = dir_funcs.get_funcs(current_function)
        else:
            func_info = dir_funcs.get_funcs("global")

        for (_, name, tipo) in decls:
            var_type = tipo_to_str(tipo)
            func_info.var_table.add_variable(name, var_type, kind='var')

        p[0] = vars_ast

def p_cycleFuncs(p):
    '''cycleFuncs :
                   | FUNCS cycleFuncs '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[1]] + p[2]

# ----- 2. Cuerpo -----
def p_CUERPO(p):
    '''CUERPO : LEFTBRACE cycleEst RIGHTBRACE'''
    p[0] = ('CUERPO', p[2])

def p_cycleEst(p):
    '''cycleEst :
                 | ESTATUTO cycleEst '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[1]] + p[2]

# ----- 3. Asigna ------
def p_ASIGNA(p):
    '''ASIGNA : ID ASSIGN EXPRESION SEMICOLON'''
    left_type = get_var_type(p[1])
    right_type = p[3][-1]
    check_types('=', left_type, right_type)

    _, address, _ = p[3]

    quad_manager.add_cuadruplo('=', address, None, p[1])

    p[0] = ('ASIGNA', p[1], p[3], left_type)

# ----- 4. CTE -----
def p_CTE_ent(p):
    '''CTE : CTE_ENT'''
    p[0] = ("cte_ent", p[1])

def p_CTE_float(p):
    '''CTE : CTE_FLOAT'''
    p[0] = ("cte_float", p[1])

# ----- 10. TIPO -----
def p_TIPO(p):
    '''TIPO : ENTERO
            | FLOTANTE'''
    if p.slice[1].type == 'ENTERO':
        p[0] = ('entero',)
    else:
        p[0] = ('flotante',)

# ----- 5. Funciones -----
def p_funcsHeader(p):
    '''funcsHeader : typeNull ID LEFTPAREN p_Follow RIGHTPAREN'''

    global current_function
    return_type = tipo_to_str(p[1])
    func_name = p[2]

    current_function = func_name

    func_info = dir_funcs.add_function(func_name, return_type)

    params = p[4]
    for param_name, tipo in params:
        param_type = tipo_to_str(tipo)
        func_info.add_parameter(param_name, param_type)

    p[0] = (p[1], func_name, params)


def p_FUNCS(p):
    '''FUNCS : funcsHeader LEFTBRACE skipVars CUERPO RIGHTBRACE SEMICOLON'''
    global current_function

    type_null, func_name, params = p[1]
    local_vars = p[3]
    cuerpo = p[4]

    current_function = None

    p[0] = ('FUNCS', type_null, func_name, params, local_vars, cuerpo)


def p_typeNull(p):
    '''typeNull : NULA
                 | TIPO'''
    p[0] = p[1]

def p_p_Follow(p):
    '''p_Follow :
                | ID COLON TIPO commaCycleFuncs '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [(p[1], p[3])] + p[4]

def p_commaCycleFuncs(p):
    '''commaCycleFuncs :
                       | COMMA p_Follow '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[2]

# ----- 6. ESTATUTO -----
def p_ESTATUTO_asigna(p):
    '''ESTATUTO : ASIGNA'''
    p[0] = p[1]

def p_ESTATUTO_condicional(p):
    '''ESTATUTO : CONDICION'''
    p[0] = p[1]

def p_ESTATUTO_ciclo(p):
    '''ESTATUTO : CICLO'''
    p[0] = p[1]

def p_ESTATUTO_llamada(p):
    '''ESTATUTO : LLAMADA SEMICOLON'''
    p[0] = ('ESTLLAMADA', p[1])

def p_ESTATUTO_imprime(p):
    '''ESTATUTO : IMPRIME'''
    p[0] = p[1]

def p_ESTATUTO_est(p):
    '''ESTATUTO : LEFTBRACKET ESTATUTO RIGHTBRACKET'''
    p[0] = ('ESTBRACKET', p[2])

# ----- 7. EXPRESION -----
def p_EXPRESION(p):
    '''EXPRESION : EXP signsExp'''
    if p[2] is None:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_signsExp(p):
    '''signsExp :
                 | GREATERTHAN EXP
                 | LESSTHAN EXP
                 | EQUAL EXP
                 | NOTEQ EXP'''
    if len(p) == 1:
        p[0] = None
    else:
        if p.slice[1].type == 'GREATERTHAN':
            op = '>'
        elif p.slice[1].type == 'LESSTHAN':
            op = '<'
        elif p.slice[1].type == 'NOTEQ':
            op = '!='
        else:
            op = '=='

        expr = relop_cuadruplo(op)
        p[0] = expr

# ----- 8. EXP -----
def p_EXP_sign(p):
    '''EXP : EXP PLUS TERMINO
           | EXP MINUS TERMINO'''
    op = '+' if p[2] == '+' else '-'
    expr = binop_cuadruplo(op)
    p[0] = expr

def p_EXP_term(p):
    '''EXP : TERMINO'''
    p[0] = p[1]

# ----- 9. TERMINO -----
def p_TERMINO_sign(p):
    '''TERMINO : TERMINO MULT FACTOR
               | TERMINO DIVIDE FACTOR'''
    op = '*' if p[2] == '*' else '/'
    expr = binop_cuadruplo(op)
    p[0] = expr

def p_TERMINO_factor(p):
    '''TERMINO : FACTOR'''
    p[0] = p[1]

# ----- 11. FACTOR -----
def p_FACTOR_exp(p):
    '''FACTOR : LEFTPAREN EXPRESION RIGHTPAREN'''
    p[0] = p[2]

def p_FACTOR_llamada(p):
    '''FACTOR : LLAMADA'''
    p[0] = p[1]

def p_FACTOR_plus(p):
    '''FACTOR : PLUS skipID'''
    p[0] = p[2]

def p_FACTOR_minus(p):
    '''FACTOR : MINUS skipID'''
    expr = unminus_cuadruplo()
    p[0] = expr

def p_FACTOR_simple(p):
    '''FACTOR : skipID'''
    p[0] = p[1]

def p_skipID(p):
    '''skipID : ID
              | CTE'''
    if p.slice[1].type == 'ID':
        var_type = get_var_type(p[1])

        quad_manager.pila_operandos.push(p[1])
        quad_manager.pila_tipos.push(var_type)

        p[0] = ("id", p[1], var_type)
    else:
        kind, value = p[1]
        const_type = 'entero' if kind == 'cte_ent' else 'flotante'

        quad_manager.pila_operandos.push(value)
        quad_manager.pila_tipos.push(const_type)

        p[0] = ("cte", value, const_type)
            

# ----- 12. LLAMADA -----
def p_LLAMADA(p):
    '''LLAMADA : ID LEFTPAREN args RIGHTPAREN'''
    func = dir_funcs.get_funcs(p[1])
    if not func:
        raise SemanticError(f"Function '{p[1]}' not declared")
    if len(p[3]) != len(func.param_types):
        raise SemanticError(f"Function '{p[1]}' expects {len(func.param_types)} arguments, got {len(p[3])}")
    
    for (arg, expected_type) in zip(p[3], func.param_types):
        arg_type = arg[-1]
        check_types('=', expected_type, arg_type)
        
    p[0] = ('LLAMADA', p[1], p[3], func.return_type)

def p_args(p):
    '''args :
            | EXPRESION argsCycle'''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[1]] + p[2]

def p_argsCycle(p):
    '''argsCycle :
                 | COMMA EXPRESION argsCycle '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[2]] + p[3]

# ----- 13. VARS -----
def p_VARS_sect(p):
    '''VARS_sect : VARS p_VARS'''
    p[0] = ('VARS', p[2])

def p_p_VARS(p):
    '''p_VARS : ID cycleID COLON TIPO SEMICOLON cycleP_VARS'''
    names = [p[1]] + p[2]
    decls = [("decl", n, p[4]) for n in names]
    p[0] = decls + p[6]

def p_cycleID(p):
    '''cycleID :
                | COMMA ID cycleID '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[2]] + p[3]

def p_cycleP_VARS(p):
    '''cycleP_VARS :
                    | p_VARS'''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]

# ----- 14. IMPRIME -----
def p_IMPRIME(p):
    '''IMPRIME : ESCRIBE LEFTPAREN imp cycleImp RIGHTPAREN SEMICOLON'''
    items = [p[3]] + p[4]

    for item in items:
        kind = item[0]
        if kind == 'letrero':
            value = item[1]
        else:
            value = item[1]

        quad_manager.add_cuadruplo('IMPRIME', value, None, None)
    p[0] = ('IMPRIME', items)

def p_imp(p):
    '''imp : LETRERO
           | EXPRESION'''
    if p.slice[1].type == 'LETRERO':
        p[0] = ("letrero", p[1], 'letrero')
    else:
        p[0] = p[1]

def p_cycleImp(p):
    '''cycleImp :
                 | COMMA imp cycleImp '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[2]] + p[3]

# ----- 15. CICLO -----
def p_CICLO(p):
    '''CICLO : MIENTRAS LEFTPAREN EXPRESION RIGHTPAREN HAZ CUERPO SEMICOLON'''
    p[0] = ("mientras", p[3], p[6])

# ----- 16. CONDICION -----
def p_CONDICION(p):
    '''CONDICION : SI LEFTPAREN EXPRESION RIGHTPAREN HAZ CUERPO sinoCuerpo SEMICOLON'''
    p[0] = ('si', p[3], p[6], p[7])

def p_sinoCuerpo(p):
    '''sinoCuerpo :
                   | SINO CUERPO '''
    if len(p) == 1:
        p[0] = None
    else:
        p[0] = ("sino", p[2])


# ----- ERROR -----
def p_error(p):
    if p:
        print(f"[SYN] Error de sintaxis en '{p.value}' (token {p.type})")
    else:
        print("[SYN] Error de sintaxis en EOF")

parser = yacc.yacc()

if __name__ == "__main__":
    data = """
    programa p;
    vars
        x : entero;
    inicio {
        escribe("Valor de x: ", x, " doble: ", x * 2);
    }

    """
    result = parser.parse(data, lexer=lexer)
    print("AST:")
    print(result)

    function_directory(dir_funcs)

    print("\nCuádruplos:")
    quad_manager.print_cuadruplos()
