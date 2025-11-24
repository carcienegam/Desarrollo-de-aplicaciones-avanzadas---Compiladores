import ply.yacc as yacc
from lex_patito import tokens, build_lexer

from semantics import FuncDirectory, SemanticError, tipo_to_str, function_directory

lexer = build_lexer()

precedence = (
    ('left', 'GREATERTHAN', 'LESSTHAN', 'EQUAL', 'NOTEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIVIDE'),
)

start = 'programa'

dir_funcs = FuncDirectory()

# ----- 1. Programa -----
def p_programa(p):
    '''programa : PROGRAMA ID SEMICOLON skipVars cycleFuncs INICIO CUERPO FIN'''
    prog_name = p[2]

    global_func = dir_funcs.add_function('global', 'nula')

    global_vars = p[4]
    if global_vars is not None:
        tag, decls = global_vars
        for (_, name, tipo) in decls:
            var_type = tipo_to_str(tipo)
            global_func.var_table.add_variable(name, var_type, kind='var')

    p[0] = ('programa', prog_name, p[4], p[5], p[7])

def p_skipVars(p):
    '''skipVars :
                  | VARS_sect '''
    if len(p) == 1:
        p[0] = None
    else:
        p[0] = p[1]

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
    p[0] = ('ASIGNA', p[1], p[3])

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
def p_FUNCS(p):
    '''FUNCS : typeNull ID LEFTPAREN p_Follow RIGHTPAREN LEFTBRACE skipVars CUERPO RIGHTBRACE SEMICOLON'''

    return_type = tipo_to_str(p[1])
    func_name = p[2]

    func_info = dir_funcs.add_function(func_name, return_type)

    params = p[4]
    for param_name, tipo in params:
        param_type = tipo_to_str(tipo)
        func_info.add_parameter(param_name, param_type)

    local_vars = p[7]
    if local_vars is not None:
        tag, decls = local_vars
        for (_, name, tipo) in decls:
            var_type = tipo_to_str(tipo)
            func_info.var_table.add_variable(name, var_type, kind='var')

    p[0] = ('FUNCS', p[1], func_name, p[4], p[7], p[8])


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
        op, right = p[2]
        p[0] = ("relop", op, p[1], right)

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
        p[0] = (op, p[2])

# ----- 8. EXP -----
def p_EXP_sign(p):
    '''EXP : EXP PLUS TERMINO
           | EXP MINUS TERMINO'''
    op = p[2]
    p[0] = ("binop", op, p[1], p[3])

def p_EXP_term(p):
    '''EXP : TERMINO'''
    p[0] = p[1]

# ----- 9. TERMINO -----
def p_TERMINO_sign(p):
    '''TERMINO : TERMINO MULT FACTOR
               | TERMINO DIVIDE FACTOR'''
    op = '*' if p[2] == '*' else '/'
    p[0] = ("binop", op, p[1], p[3])

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
    p[0] = ("unop", '-', p[2])

def p_FACTOR_simple(p):
    '''FACTOR : skipID'''
    p[0] = p[1]

def p_skipID(p):
    '''skipID : ID
              | CTE'''
    if p.slice[1].type == 'ID':
        p[0] = ("id", p[1])
    else:
        p[0] = p[1]

# ----- 12. LLAMADA -----
def p_LLAMADA(p):
    '''LLAMADA : ID LEFTPAREN args RIGHTPAREN'''
    p[0] = ('LLAMADA', p[1], p[3])

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
    p[0] = ('IMPRIME', [p[3]] + p[4])

def p_imp(p):
    '''imp : LETRERO
           | EXPRESION'''
    if p.slice[1].type == 'LETRERO':
        p[0] = ("letrero", p[1])
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
        x, y : entero;
        z : flotante;

    entero suma(a : entero, b : entero) {
        {
            escribe(a + b);
        }
    };
    nula foo() {
        {
            escribe("en foo");
        }
    };
    inicio {
        x = 3;
        y = x + 5;
        z = 1.5;
        suma(x, y);
        foo();
    }
    fin
    """
    result = parser.parse(data, lexer=lexer)
    print("AST:")
    print(result)

    function_directory(dir_funcs)
