# -----------------------------------------------------------------------------
#
#
#
# -----------------------------------------------------------------------------
import re
import ply.yacc as yacc
from .parsing_classes import Var, Indic
import logging

logger = logging.getLogger(__name__)
separators = ['RE-MIN', 'RE-MAX', 'TB', 'TE', 'CAL']
tokens = [
    'VARIABLE','NUMBER', 'INDICATOR', 'POP',
    'PLUS','MINUS','TIMES','DIVIDE', 'POW',
    'LPAREN','RPAREN',
    'PARAM', 'SEPARATOR'
    ]

return_values = []
indicators = []
variables = []

# Tokens

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_POW     = r'\^'
t_VARIABLE = r'((C)|(D)|(SC)|(SD))[0-9]+'
t_INDICATOR = r'[A-Z0-9]+(_[A-Z0-9]+)+'
t_POP = r'\$POP'

def t_PARAM(t):
    r"""\[[A-Z:\s0-9#\-]+\]"""  #On récupère les éléments entre crochets (Les paramètres)
    global separators
    split_parameter = re.search(r'([A-Z\-]+)\s*:\s*([A-Z0-9#]+)', t.value[1:-1])
    t.value = (split_parameter.group(1), split_parameter.group(2))

    if t.value[0] in separators:
        t.type = 'SEPARATOR'
    return t

def t_NUMBER(t):
    r"""\d+"""
    t.value = int(t.value)
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    logger.debug("Illegal character '%s'" % t.value[0])
    raise Exception("Illegal character '%s'" % t.value[0])

# Build the lexer
import ply.lex as lex
lex.lex()

# Precedence rules for the arithmetic operators
precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE', 'POW'),
    ('right','UMINUS', 'UPLUS'),
    )

def p_bloc(p):
    """
    start : expression
          | expression separator
          | expression separator start
    """
    global return_values

    p[1] = {'tree': p[1], 'exmin': None, 'exmax': None, 'typeBudget': None,  'CAL': None, 'TE': None}

    if len(p) > 2:
        #Il y a des séparateurs, donc potentiellement des exmin/exmax
        for separator in p[2]:
            if separator[0] == 'RE-MIN':
                p[1]['exmin'] = separator[1] if separator[1] != '#' else None
            elif separator[0] == 'RE-MAX':
                p[1]['exmax'] = separator[1] if separator[1] != '#' else None
            elif separator[0] == 'CAL':
                p[1]['CAL'] = separator[1]
            elif separator[0] == 'TB':
                p[1]['typeBudget'] = separator[1]
            elif separator[0] == 'TE':
                p[1]['TE'] = separator[1]

    return_values.append(p[1])

def p_expression_binop(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression POW expression
                  """
    left_child = p[1]
    right_child = p[3]

    if p[2] == '+'  : p[0] = ('+', left_child, right_child)
    elif p[2] == '-': p[0] = ('-', left_child, right_child)
    elif p[2] == '*': p[0] = ('*', left_child, right_child)
    elif p[2] == '/': p[0] = ('/', left_child, right_child)
    elif p[2] == '^': p[0] = ('^', left_child, right_child)
    
def p_expression_parameter(p):
    """
        expression : expression parameter
    """
    p[0] = p[1]

def p_expression_uminus(p):
    """expression : MINUS expression %prec UMINUS"""
    p[2].minus = True
    p[0] = p[2]

def p_expression_uplus(p):
    """expression : PLUS expression %prec UPLUS"""
    p[0] = p[2]

def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]

def p_expression_number(p):
    """expression : NUMBER"""
    p[0] = p[1]

def p_expression_indicator(p):
    """expression : INDICATOR"""
    global indicators

    indic = Indic(p[1], None, False)
    indicators.append(indic)
    p[0] = indic

def p_expression_variable(p):
    """expression : VARIABLE"""
    global variables

    var = Var(p[1], None, False)
    variables.append(var)
    p[0] = var

def p_expression_population(p):
    """expression : POP"""

    p[0] = p[1]

def p_separator(p):
    """
    separator : SEPARATOR separator
              | SEPARATOR
    """
    if len(p) == 3:
        if type(p[2]) is list:
            p[2].append(p[1])
            p[0] = p[2]
    else:
        p[0] = [p[1]]

def p_parameter(p):
    """parameter : PARAM"""
    global variables
    global indicators

    if p[1][0] == 'TA':
        for variable in variables:
            variable.type_solde = p[1][1]
        variables = []
    elif p[1][0] == 'OS':
        indicators[len(indicators) - 1].offset = p[1][1]
        indicators = []
    p[0] = p[1]

def p_error(p):
    logger.debug("Syntax error at '%s'" % p.value)
    raise Exception("Syntax error at '%s'" % p.value)


yacc.yacc()

def check_equation(tree):
    offset_regex = re.compile(r'^[MP][0-9]{1,2}$')
    if type(tree) is Var:
        if tree.type_solde is None:
            raise Exception(f"La variable {tree.name} ne possède pas de type d'appel [TA: …] \n"
                            f"Valeurs acceptées : {str(Var.LIST_TYPE_APPEL)[1:-1]}")
        elif tree.type_solde not in Var.LIST_TYPE_APPEL:
            raise Exception(f"La variable {tree.name} possède un type d'appel incorrect : {tree.type_solde}\n"
                            f"Valeurs acceptées : {str(Var.LIST_TYPE_APPEL)[1:-1]}")
    elif type(tree) is Indic:
        if tree.offset is not None and not offset_regex.match(tree.offset):
            raise Exception(f"L'indicateur {tree.name} possède un décalage annuel incorrect : {tree.offset}\n"
                            f"Valeurs acceptées : M1 ou P9")
    elif type(tree) is tuple:
        check_equation(tree[1])
        check_equation(tree[2])

def check_type_budget(parsed_equation):
    if parsed_equation['typeBudget'] is not None and parsed_equation['typeBudget'] not in ['BP', 'BA']:
        raise Exception(f"Le type de budget de l'équation n'est pas correct : {parsed_equation['typeBudget']}\n"
                        f"Valeurs acceptées : 'BP' ou 'BA'")

def parse_equation(eq):
    global return_values
    global indicators
    global variables

    return_values = []
    indicators = []
    variables = []
    yacc.parse(eq)

    for value in return_values:
        check_type_budget(value)
        check_equation(value['tree'])
    return return_values