import ply.lex as lex

# Palabras reservadas
reserved = {
    'programa' : 'PROGRAMA',
    'main'   : 'MAIN',
    'end'      : 'END',
    'vars'     : 'VARS',
    'int'   : 'INT',
    'float' : 'FLOAT',
    'nula'     : 'NULA',
    'print'  : 'PRINT',
    'while' : 'WHILE',
    'do'      : 'DO',
    'if'       : 'IF',
    'else'     : 'ELSE',
    'return'   : 'RETURN',
}

#Lista de tokens
tokens = [
    'ID',
    'CTE_INT',
    'CTE_FLOAT',
    'LETRERO',

    # Operadores
    'PLUS',
    'MINUS',
    'MULT',
    'DIVIDE',
    'GREATERTHAN',
    'LESSTHAN',
    'EQUAL',
    'NOTEQ',
    'ASSIGN',

    # Simbolos
    'SEMICOLON',
    'COMMA',
    'COLON',
    'LEFTBRACE',
    'RIGHTBRACE',
    'LEFTPAREN',
    'RIGHTPAREN',
    'LEFTBRACKET',
    'RIGHTBRACKET',
] + list(reserved.values())


# Reglas de expresiones regulares para tokens simples

# Operadores
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIVIDE = r'/'
t_GREATERTHAN = r'>'
t_LESSTHAN = r'<'
t_EQUAL = r'=='
t_NOTEQ = r'!='
t_ASSIGN = r'='

# Simbolos
t_SEMICOLON = r';'
t_COMMA = r','
t_COLON = r':'
t_LEFTBRACE = r'\{'
t_RIGHTBRACE = r'\}'
t_LEFTPAREN = r'\('
t_RIGHTPAREN = r'\)'
t_LEFTBRACKET = r'\['
t_RIGHTBRACKET = r'\]'

# Ignorar espacios y tabs
t_ignore = ' \t'

def t_COMMENT(t):
    r'//.*'
    pass

def t_CTE_FLOAT(t):
    r'-?\d*\.\d+'
    t.value = float(t.value)
    return t

def t_CTE_INT(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

def t_LETRERO(t): #strings
    r'"[^"\n]*"'
    t.value = t.value[1:-1]
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID') # Si es palabra reservada uso el token reservado
    return t

def t_newline(t): # saltos de linea
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

def build_lexer(**kwargs):
    return lex.lex(**kwargs)

if __name__ == "__main__":
    data = """
    programa p;
    vars
        x : entero;
    inicio {
        x = 10;
        escribe("Valor de x: ", x, " doble: ", x * 2);
    }
    fin

    """

    lexer = build_lexer()
    lexer.input(data)
    for tok in lexer:
        print(tok)

