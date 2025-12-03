import ply.yacc as yacc
from lex_patito import tokens, build_lexer

from semantics import FuncDirectory, SemanticError, tipo_to_str, function_directory, vm
from semantic_cube import check_types

from quads import QuadManager

lexer = build_lexer()

# precedence = (
#     ('left', 'GREATERTHAN', 'LESSTHAN', 'EQUAL', 'NOTEQ'),
#     ('left', 'PLUS', 'MINUS'),
#     ('left', 'MULT', 'DIVIDE'),
# )

start = 'programa'

dir_funcs = FuncDirectory()

current_function = None
dir_funcs.add_function("global", "nula")
current_func_call = None # FunctionInfo de la funcion que estoy llamando
current_param_idx = 0 # Index de param actual

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

def get_var_info(name):
    if current_function and dir_funcs.exists(current_function):
        t = dir_funcs.get_funcs(current_function).var_table.get_vars(name)
        if t:
            return t

    g = dir_funcs.get_funcs("global").var_table.get_vars(name)
    if g:
        return g

    raise SemanticError(f"Variable '{name}' not declared")

def binop_cuadruplo(op):
    # Cuadruplos para operaciones binarias (+, -, *, /)
    right = quad_manager.pila_operandos.pop()
    right_type = quad_manager.pila_tipos.pop()
    left = quad_manager.pila_operandos.pop()
    left_type = quad_manager.pila_tipos.pop()

    result_type = check_types(op, left_type, right_type)
    temporal_address = quad_manager.new_temporal(result_type)
    quad_manager.add_cuadruplo(op, left, right, temporal_address)

    quad_manager.pila_operandos.push(temporal_address)
    quad_manager.pila_tipos.push(result_type)

    return ('temp', temporal_address, result_type)

def relop_cuadruplo(op):
    # Cuadruplos para operaciones relacionales (<, >, ==, !=)
    right = quad_manager.pila_operandos.pop()
    right_type = quad_manager.pila_tipos.pop()
    left = quad_manager.pila_operandos.pop()
    left_type = quad_manager.pila_tipos.pop()

    print("\nDEBUG relop:")
    print(" left:", left, left_type)
    print(" right:", right, right_type)


    result_type = check_types(op, left_type, right_type)
    temporal_address = quad_manager.new_temporal(result_type)
    quad_manager.add_cuadruplo(op, left, right, temporal_address)

    quad_manager.pila_operandos.push(temporal_address)
    quad_manager.pila_tipos.push(result_type)

    return ('temp', temporal_address, result_type)

def unminus_cuadruplo():
    # Cuadruplos para operación unaria (-)
    operand = quad_manager.pila_operandos.pop()
    operand_type = quad_manager.pila_tipos.pop()

    temporal_address = quad_manager.new_temporal(operand_type)
    quad_manager.add_cuadruplo('uminus', operand, None, temporal_address)

    quad_manager.pila_operandos.push(temporal_address)
    quad_manager.pila_tipos.push(operand_type)

    return ('temp', temporal_address, operand_type)


# ----- 1. Programa -----
def p_programa_start(p):
    '''program_start : PROGRAMA'''
    global quad_manager, dir_funcs
    if dir_funcs.get_funcs('global') is None:
        dir_funcs.add_function('global', 'nula')

    p.parser.goto_main_idx = quad_manager.add_cuadruplo('GOTO', None, None, None)

def p_main_start(p):
    '''main_start : START'''
    global dir_funcs, quad_manager
    dir_funcs.get_funcs('global').start_quad = len(quad_manager.cuadruplos)
    
def p_programa(p):
    '''programa : program_start ID SEMICOLON skipVars cycleFuncs main_start CUERPO END'''
    global dir_funcs, quad_manager

    main_start = dir_funcs.get_funcs('global').start_quad

    quad_manager.fill_cuadruplos(p.parser.goto_main_idx, main_start)

    quad_manager.add_cuadruplo('END', None, None, None)

    p[0] = ('programa', p[2])

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
    left_info = get_var_info(p[1])
    left_type = get_var_type(p[1])
    left_address = left_info.address

    right_type = p[3][-1]
    check_types('=', left_type, right_type)

    _, right_address, _ = p[3]

    quad_manager.add_cuadruplo('=', right_address, None, left_address)

    p[0] = ('ASIGNA', left_address, p[3], left_type)

# ----- 4. CTE -----
def p_CTE_ent(p):
    '''CTE : CTE_INT'''
    p[0] = ("cte_int", p[1])

def p_CTE_float(p):
    '''CTE : CTE_FLOAT'''
    p[0] = ("cte_float", p[1])

# ----- 10. TIPO -----
def p_TIPO(p):
    '''TIPO : INT
            | FLOAT'''
    if p.slice[1].type == 'INT':
        p[0] = ('int',)
    else:
        p[0] = ('float',)

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
    '''FUNCS : funcsHeader LEFTBRACE skipVars func_start CUERPO func_end RIGHTBRACE SEMICOLON'''
    global current_function

    type_null, func_name, params = p[1]
    local_vars = p[3]
    cuerpo = p[5]

    current_function = None

    p[0] = ('FUNCS', type_null, func_name, params, local_vars, cuerpo)

def p_func_start(p):
    '''func_start :'''
    func_name = current_function
    func_info = dir_funcs.get_funcs(func_name)
    func_info.start_quad = len(quad_manager.cuadruplos)

    vm.reset_temporals()

def p_func_end(p):
    '''func_end :'''
    quad_manager.add_cuadruplo('ENDFUNC', None, None, None)

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

def p_ESTATUTO_return(p):
    '''ESTATUTO : RETURN EXPRESION SEMICOLON'''
    global current_function

    if current_function is None:
        raise SemanticError("Return not in function")
    
    func_info = dir_funcs.get_funcs(current_function)
    func_ret_type = func_info.return_type

    if func_ret_type is None or func_ret_type == 'nula':
        raise SemanticError(f"Function '{current_function}' is void")
    
    _, expr_address, expr_type = p[2]
    check_types('=', func_ret_type, expr_type)

    if func_info.return_address is None:
        raise SemanticError(f"No return address assigned")

    quad_manager.add_cuadruplo('RETURN', None, None, expr_address)

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
        var_info = get_var_info(p[1])
        var_type = get_var_type(p[1])
        address = var_info.address

        quad_manager.pila_operandos.push(address)
        quad_manager.pila_tipos.push(var_type)

        p[0] = ("id", address, var_type)
    else:
        kind, value = p[1]
        const_type = 'int' if kind == 'cte_int' else 'float'
        const_address = vm.get_constant(value, const_type)

        quad_manager.pila_operandos.push(const_address)
        quad_manager.pila_tipos.push(const_type)

        p[0] = ("cte", const_address, const_type)
            

# ----- 12. LLAMADA -----
def p_LLAMADA(p):
    '''LLAMADA : ID ERA LEFTPAREN args RIGHTPAREN'''
    global current_func_call, current_param_idx

    func_name = p[1]
    func = current_func_call
    if func is None:
        func = dir_funcs.get_funcs(func_name)
        if not func:
            raise SemanticError("Function '{func_name}' not declared")
        
    if current_param_idx != len(func.param_types):
        raise SemanticError(f"Function '{func_name}' expects {len(func.param_types)} arguments, got {current_param_idx}")
    
    quad_manager.add_cuadruplo('GOSUB', None, None, func_name)

    # parche gualadupano! si la funcion tiene return la guardamos en un temporal
    if func.return_type is not None and func.return_type != 'nula':
        if func.return_address is None:
            raise SemanticError(f"Function '{func_name}' has no return_address")
        
        temp_address = quad_manager.new_temporal(func.return_type)
        quad_manager.add_cuadruplo('=', func.name, None, temp_address)

        quad_manager.pila_operandos.push(temp_address)
        quad_manager.pila_tipos.push(func.return_type)

        result = ('temp', temp_address, func.return_type)
    else:
        result = ('call', func_name, None, 'nula')


    # Reset estados de llamada
    current_func_call = None
    current_param_idx = 0

    p[0] = result

def p_ERA(p):
    '''ERA :'''
    global current_func_call, current_param_idx
    func_name = p[-1]
    func = dir_funcs.get_funcs(func_name)
    if not func:
        raise SemanticError(f"Function '{func_name}' not declared")
    
    current_func_call = func
    current_param_idx = 0

    quad_manager.add_cuadruplo('ERA', None, None, func_name)

def p_args(p):
    '''args :
            | arg_item argsCycle'''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[1]] + p[2]

def p_argsCycle(p):
    '''argsCycle :
                 | COMMA arg_item argsCycle '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[2]] + p[3]

def p_arg_item(p):
    '''arg_item : EXPRESION'''
    global current_param_idx, current_func_call

    expr = p[1]
    if current_func_call is None:
        raise SemanticError("Out of context argument in function call")
    
    _, arg_address, arg_type = expr

    if current_param_idx >= len(current_func_call.param_types):
        raise SemanticError("Too many arguments for function '{current_func_call.name}'")
    
    expected_type = current_func_call.param_types[current_param_idx]
    check_types('=', expected_type, arg_type)

    param_count = f"P{current_param_idx + 1}"
    quad_manager.add_cuadruplo('PARAM', arg_address, None, param_count)

    quad_manager.pila_operandos.pop()
    quad_manager.pila_tipos.pop()

    current_param_idx += 1

    p[0] = expr

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
    '''IMPRIME : PRINT LEFTPAREN imp cycleImp RIGHTPAREN SEMICOLON'''
    items = [p[3]] + p[4]

    for item in items:
        address = item[1]
        quad_manager.add_cuadruplo('IMPRIME', address, None, None)

    p[0] = ('IMPRIME', items)

def p_imp(p):
    '''imp : LETRERO
           | EXPRESION'''
    if p.slice[1].type == 'LETRERO':
        address = vm.get_constant(p[1], 'letrero')
        p[0] = ("letrero", address, 'letrero')
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
    '''CICLO : WHILE ciclo_start LEFTPAREN EXPRESION RIGHTPAREN ciclo_goToF DO CUERPO ciclo_end SEMICOLON'''
    p[0] = ("while", p[4], p[8])

def p_ciclo_start(p):
    '''ciclo_start :'''
    start_idx =  len(quad_manager.cuadruplos)
    quad_manager.pila_saltos.push(start_idx)

def p_ciclo_goToF(p):
    '''ciclo_goToF :'''
    cond_address = quad_manager.pila_operandos.pop()
    cond_type = quad_manager.pila_tipos.pop()

    if cond_type != 'bool':
        raise SemanticError("Condicion 'while' debe ser tipo bool")
    
    goToF_idx = quad_manager.add_cuadruplo('GOTOF', cond_address, None, None)
    quad_manager.pila_saltos.push(goToF_idx)

def p_ciclo_end(p):
    '''ciclo_end :'''
    goToF_idx = quad_manager.pila_saltos.pop()
    start_idx = quad_manager.pila_saltos.pop()
    quad_manager.add_cuadruplo('GOTO', None, None, start_idx)

    exit_idx = len(quad_manager.cuadruplos)
    quad_manager.fill_cuadruplos(goToF_idx, exit_idx)


# ----- 16. CONDICION -----
def p_CONDICION_if(p):
    '''CONDICION : IF LEFTPAREN EXPRESION RIGHTPAREN if_goToF CUERPO if_noElse SEMICOLON'''
    p[0] = ('if', p[3], p[6], None)

def p_CONDICION_ifelse(p):
    '''CONDICION : IF LEFTPAREN EXPRESION RIGHTPAREN if_goToF CUERPO ELSE if_else CUERPO if_else_end SEMICOLON'''
    p[0] = ('if', p[3], p[6], p[9])

def p_if_goToF(p):
    '''if_goToF :'''
    cond_address = quad_manager.pila_operandos.pop()
    cond_type = quad_manager.pila_tipos.pop()

    if cond_type != 'bool':
        raise SemanticError("Condicion 'if' debe ser tipo bool")
    
    goToF_idx = quad_manager.add_cuadruplo('GOTOF', cond_address, None, None)
    quad_manager.pila_saltos.push(goToF_idx)

def p_if_noElse(p):
    '''if_noElse :'''
    goToF_idx = quad_manager.pila_saltos.pop()
    exit_idx = len(quad_manager.cuadruplos)
    quad_manager.fill_cuadruplos(goToF_idx, exit_idx)

def p_if_else(p):
    '''if_else :'''
    goTo_idx = quad_manager.add_cuadruplo('GOTO', None, None, None)
    goToF_idx = quad_manager.pila_saltos.pop()
    quad_manager.fill_cuadruplos(goToF_idx, len(quad_manager.cuadruplos))

    quad_manager.pila_saltos.push(goTo_idx)

def p_if_else_end(p):
    '''if_else_end :'''
    goTo_idx = quad_manager.pila_saltos.pop()
    exit_idx = len(quad_manager.cuadruplos)
    quad_manager.fill_cuadruplos(goTo_idx, exit_idx)

# ----- ERROR -----
def p_error(p):
    if p:
        print(f"[SYN] Error de sintaxis en '{p.value}' (token {p.type})")
    else:
        print("[SYN] Error de sintaxis en EOF")

parser = yacc.yacc()

if __name__ == "__main__":
    data = """
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

    start {
        i = 2;
        j = i * 2 - 1;
        uno(j);
        print(i + dos(i + j));
    }
    end


    """


    result = parser.parse(data, lexer=lexer)
    print("AST:")
    print(result)

    function_directory(dir_funcs)

    print("\nCuádruplos con direcciones:")
    quad_manager.print_cuadruplos()

    print("\nCuádruplos:")
    quad_manager.print_cuadruplos_symbolic(dir_funcs, vm)

