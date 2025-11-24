from semantics import SemanticError

INT = 'entero'
FLOAT = 'flotante'
BOOL = 'bool'
STRING = 'letrero'

semantic_cube = {

    '+': {
        INT: {INT: INT, FLOAT: FLOAT},
        FLOAT: {INT: FLOAT, FLOAT: FLOAT},
    },

    '-': {
        INT: {INT: INT, FLOAT: FLOAT},
        FLOAT: {INT: FLOAT, FLOAT: FLOAT},
    },

    '*': {
        INT: {INT: INT, FLOAT: FLOAT},
        FLOAT: {INT: FLOAT, FLOAT: FLOAT},
    },

    '/': {
        INT: {INT: FLOAT, FLOAT: FLOAT},
        FLOAT: {INT: FLOAT, FLOAT: FLOAT},
    },

    '<': {
        INT: {INT: BOOL, FLOAT: BOOL},
        FLOAT: {INT: BOOL, FLOAT: BOOL},
    },

    '>': {
        INT: {INT: BOOL, FLOAT: BOOL},
        FLOAT: {INT: BOOL, FLOAT: BOOL},
    },

    '==': {
        INT: {INT: BOOL, FLOAT: BOOL},
        FLOAT: {INT: BOOL, FLOAT: BOOL},
        BOOL: {BOOL: BOOL},
        STRING: {STRING: BOOL},
    },

    '!=': {
        INT: {INT: BOOL, FLOAT: BOOL},
        FLOAT: {INT: BOOL, FLOAT: BOOL},
        BOOL: {BOOL: BOOL},
        STRING: {STRING: BOOL},
    },

    '=': {
        INT: {INT: INT},
        FLOAT: {INT: FLOAT, FLOAT: FLOAT},
        BOOL: {BOOL: BOOL},
        STRING: {STRING: STRING},
    }
}

def check_types(op, left_type, right_type):
    try:
        return semantic_cube[op][left_type][right_type]
    except KeyError:
        raise SemanticError(f"Invalid operation: {left_type} {op} {right_type}")