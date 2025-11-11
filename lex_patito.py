import re
import ply.lex as lex

# Palabras reservadas
reserved = {
    'program': 'PROGRAM',
    'main': 'MAIN',
    'end': 'END',
    'var': 'VAR',
    'int': 'INT',
    'float': 'FLOAT',
    'void': 'VOID',
    'print': 'PRINT',
    'while': 'WHILE',
    'do': 'DO',
    'if': 'IF',
    'else': 'ELSE',
}

# Tokens
tokens = [
    'ID', 'CTE_INT', 'CTE_FLOAT', 'CTE_STRING', 
    'SEMI', 'LBRACE', 'RBRACE', 'ASSIGN', 
    'GTHAN', 'LTHAN', 'NOTEQ', 'LPAREN', 'RPAREN', 
    'COMMA', 'COLON', 'LBRACKET', 'RBRACKET', 'PLUS', 'MINUS', 'MULT', 'DIV',
] + list(reserved.values())

# Expresiones regulares simples
t_SEMI      = r';'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_ASSIGN    = r'='
t_GTHAN     = r'>'
t_LTHAN     = r'<'
t_NOTEQ       = r'!='
t_LPAREN    = r'\('
t_RPAREN   = r'\)'
t_COMMA     = r','
t_COLON     = r':'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_MULT      = r'\*'
t_DIV       = r'/'

# ER numeros y strings
def t_CTE_FLOAT(t):
    r'-?\d*\.\d+'
    t.value = float(t.value)
    return t

def t_CTE_INT(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

def t_CTE_STRING(t):
    r'"[^"\n]*"'
    t.value = t.value[1:-1]
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Ignorar espacios y tabs, comentarios

def t_comment(t):
    r'\/\/[^\n]*'
    pass

t_ignore = ' \t\r\f\v'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    raise SyntaxError(f"Illegal character '{t.value[0]}' at line {t.lineno}")

def build_lexer(**kwargs):
    return lex.lex(**kwargs)
