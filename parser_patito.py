import ply.yacc as yacc
from lex_patito import tokens, build_lexer

precedence = (
    ('left', 'GTHAN', 'LTHAN', 'NOTEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIV'),
)

# Helpers

def BinOp(op, a, b):
    return ('binOp', op, a, b)

def UnOp(op, a):
    return ('unOp', op, a)

def Assign(id, expr):
    return ('assign', id, expr)

def Print(expr):
    return ('print', expr)

def While(expr, body):
    return ('while', expr, body)

def If(expr, then_body, else_body):
    return ('if', expr, then_body, else_body)

def Block(stmts):
    return ('block', stmts)

def Id(name):
    return ('id', name)

def Cte(type, value):
    return ('cte', type, value)

def VDecl(name, type):
    return ('vdecl', name, type)

def Param(name, type):
    return ('param', name, type)

def Func(name, params, decloc, body):
    return ('func', name, params, decloc, body)

def Program(n, vdecls, fdecls, body):
    return ('program', n, vdecls, fdecls, body)


# Gramatica


def p_start(p):
    'start : programa'
    p[0] = p[1]


# 1. ----- PROGRAMA
# <PROGRAMA> -> program id ; <skip_Vars> <skip_Funcs> main <BODY> end
def p_programa(p):
    'programa : PROGRAM ID SEMI skip_Vars skip_Funcs MAIN body END'
    p[0] = Program(p[2], p[4] or [], p[5] or [], p[7])

# <skip_V'> -> <VARS> | empty
def p_skip_Vars(p):
    ''' skip_Vars : vars
                  | empty '''
    p[0] = p[1]

# <skip_F'> -> <loop_F> | empty
def p_skip_Funcs(p):
    ''' skip_Funcs : loop_Funcs
                   | empty '''
    p[0] = p[1]

# <loop_F> -> <FUNCS><loop_F>
def p_loop_Funcs(p):
    ''' loop_Funcs : func
                   | loop_Funcs func '''
    p[0] = p[1] if len(p) == 2 else p[1] + [p[2]]


# 2. ----- BODY
# <BODY> -> { <skip_S'> }
def p_body(p):
    'body : LBRACE skip_s_p RBRACE'
    p[0] = Block(p[2] or [])

# <skip_S'> -> empty | <STATEMENT><skip_S'>
def p_skip_s_p(p):
    ''' skip_s_p : empty
                   | skip_s_p stmt '''
    p[0] = [] if len(p) == 2 else p[1] + [p[2]]


# 3. ----- STATEMENT
# <STATEMENT> -> <ASSIGN> | <CONDITION> | <CYCLE> | <F_CALL> | <PRINT>
def p_statement(p):
    ''' stmt : assign
             | condition
             | cycle
             | f_call
             | print '''
    p[0] = p[1]

# 4. ----- ASSIGN
# <ASSIGN> -> id = <EXP> ;
def p_assign(p):
    'assign : ID ASSIGN exp SEMI'
    p[0] = Assign(Id(p[1]), p[3])

# 5. ----- EXPRESION
# <EXPRESION> -> <EXP><E'>
def p_expresion(p):
    'expresion : exp e_p'
    p[0] = p[1] if p[2] is None else BinOp(p[2][0], p[1], p[2][1])

# <E'> -> > <EXP> | < <EXP> | != <EXP> | empty
def p_e_p(p):
    ''' e_p : GTHAN exp
            | LTHAN exp
            | NOTEQ exp
            | empty '''
    p[0] = None if len(p) == 2 else (p[1], p[2])

# 7. ----- EXP
# <EXP> -> <TERMINO><loop_SoR'>
def p_exp(p):
    '''exp : termino
           | exp PLUS termino
           | exp MINUS termino'''
    p[0] = p[1] if len(p) == 2 else BinOp(p[2], p[1], p[3])

# 8. ----- TERMINO
# <TERMINO> -> <FACTOR><loop_MoD'>
def p_termino(p):
    '''termino : factor
               | termino MULT factor
               | termino DIV factor'''
    p[0] = p[1] if len(p) == 2 else BinOp(p[2], p[1], p[3])

# 15. ----- FACTOR
# <FACTOR> -> ( <EXPRESION> )
# <FACTOR> -> <skip_SoR'><skip_id'>
# <skip_SoR'> -> + | - | empty
# <skip_id'> -> id | <CTE>

def p_factor(p):
    'factor : LPAREN expresion RPAREN'
    p[0] = p[2]

def p_factor2(p):
    ''' factor : skip_SoR skip_id 
                | skip_id '''
    p[0] = p[1] if len(p)==2 else (p[2] if p[1]=='UPLUS' else UnOp('UMINUS', p[2]))

def p_skip_SoR(p):
    ''' skip_SoR : PLUS
                  | MINUS
                  | empty '''
    if len(p) == 2 and p[1] is None:
        p[0] = None
    else:
        p[0] = 'UPLUS' if p.slice[1].type == 'PLUS' else 'UMINUS'

def p_skip_id(p):
    ''' skip_id : ID
                 | CTE_INT
                 | CTE_FLOAT '''
    
    t = p.slice[1].type
    if t == 'ID':
        p[0] = Id(p[1])
    elif t == 'CTE_INT':
        p[0] = Cte('CTE_INT', p[1])
    else:
        p[0] = Cte('CTE_FLOAT', p[1])

# 10. ----- VARS
# <VARS> -> var <V'><v_loop'>
def p_vars(p):
    '''vars : VAR v_p v_loop_p'''
    p[0] = [p[2]] + p[3]

def p_v_p(p):
    'v_p : ID c_loop_id COLON type SEMI'
    p[0] = VDecl([p[1]] + p[2], p[4])

def p_c_loop_id(p):
    '''c_loop_id : c_loop_id COMMA ID
                 | empty '''
    p[0] = [] if len(p) == 2 else p[1] + [p[3]]

def p_v_loop_p(p):
    '''v_loop_p : empty
                 | v_loop_p v_p '''
    p[0] = [] if len(p) == 2 else p[1] + [p[2]]

# 11. ----- TYPE
# <TYPE> -> INT | FLOAT
def p_type(p):
    '''type : INT
            | FLOAT'''
    p[0] = 'int' if p.slice[1].type=='INT' else 'float'

# 9. ----- FUNCS
# <FUNCS> -> void id ( <F’> <c_rep’> ) [ <f_V’> <Body> ] ;
def p_func(p):
    'func : VOID ID LPAREN f_p c_rep_p RPAREN LBRACKET f_v_p body RBRACKET SEMI'
    name = p[2]
    params = ([] if p[4] is None else [p[4]]) + p[5]
    decloc = p[8] or []
    p[0] = Func(name, params, decloc, p[9])

# <F'> -> <f_c> | empty
def p_f_p(p):
    ''' f_p : f_c
            | empty '''
    p[0] = p[1]

# <f_c> -> id : <TYPE>
def p_f_c(p):
    'f_c : ID COLON type'
    p[0] = Param(p[1], p[3])

# <c_rep'> -> , <f_c> | empty
def p_c_rep_p(p):
    ''' c_rep_p : empty
                 | c_rep_p COMMA f_c '''
    p[0] = [] if len(p) == 2 else p[1] + [p[3]]

# <f_V'> -> <VARS> | empty
def p_f_v_p(p):
    ''' f_v_p : vars
               | empty '''
    p[0] = p[1]

# 12. ----- Print
# <PRINT> -> print ( <P'> <c_loop'> ) ;
def p_print(p):
    'print : PRINT LPAREN p_p c_loop_print RPAREN SEMI'
    first = [] if p[3] is None else [p[3]]
    p[0] = Print(first + p[4])

# <P'> -> <EXPRESION> | cte.string
def p_p_p(p):
    ''' p_p : expresion
            | CTE_STRING '''
    if p.slice[1].type == 'CTE_STRING':
        p[0] = Cte('CTE_STRING', p[1])
    else:
        p[0] = p[1]

# <c_loop'> -> , <P'> | empty
def p_c_loop_print(p):
    ''' c_loop_print : empty
                  | c_loop_print COMMA p_p '''
    p[0] = [] if len(p) == 2 else p[1] + [p[3]]

# 13. ----- CYCLE
# <CYCLE> -> while ( <EXPRESION> ) do <BODY> ;
def p_cycle(p):
    'cycle : WHILE LPAREN expresion RPAREN DO body SEMI'
    p[0] = While(p[3], p[6])

# 14. ----- CONDITION
# <CONDITION> -> if ( <EXPRESION> ) <BODY> <C'> ;
def p_condition(p):
    'condition : IF LPAREN expresion RPAREN body c_p SEMI'
    p[0] = If(p[3], p[5], p[6])

# <C'> -> else <BODY> | empty
def p_c_p(p):
    ''' c_p : ELSE body
             | empty '''
    p[0] = None if len(p) == 2 else p[2]


# 16. ----- F_Call

# <F_CALL> -> id ( <skip_E'> ) ;
def p_f_call(p):
    'f_call : ID LPAREN skip_e_p RPAREN SEMI'
    p[0] = ('f_call', p[1], p[3])

# <skip_E'> -> <EXPRESION><c_loop'> | empty
def p_skip_e_p(p):
    ''' skip_e_p : empty
                  | expresion c_loop_p '''
    p[0] = [] if p[1] is None else [p[1]] + p[2]

def p_c_loop_p(p):
    ''' c_loop_p : empty
                  | c_loop_p COMMA expresion '''
    p[0] = [] if len(p) == 2 else p[1] + [p[3]]


# ----- VACIO -----
def p_empty(p):
    'empty :'
    p[0] = None

# ----- ERRORES -----
def p_error(p):
    if p is None:
        raise SyntaxError("Syntax error at EOF")
    raise SyntaxError(f"Syntax error at '{p.value}' (line {p.lineno})")

def build_parser():
    lexer = build_lexer()
    parser = yacc.yacc(start='start')
    return lexer, parser

