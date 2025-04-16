import ply.lex as lex

# Reserved words
reserved = {
    'func': 'FUNC',   # Function definition
    'if': 'IF',   # If statement
    'else': 'ELSE',   # Else statement
    'while': 'WHILE',   # While loop
    'repeat': 'REPEAT',  # Repeat loop
    'move': 'MOVE',   # Move action
    'turn_left': 'TURN_LEFT',   # Turn left action
    'turn_right': 'TURN_RIGHT',   # Turn right action
    'pickup': 'PICKUP',   # Pickup action
    'drop': 'DROP',  # Drop action
    'see': 'SEE',  # See action
    'read': 'READ',  # Read action
    'write': 'WRITE',  # Write action
    'wait': 'WAIT'  # Wait action
}


# List of token names
tokens = [
    'IDENTIFIER',  # Strings of characters
    'NUMBER',  # Integer numbers
    'ASSIGN',  # Assignment operator =
    'SEMICOLON',  # Statement terminator ;
    'LPAREN',   # Left parenthesis (
    'RPAREN',  # Right parenthesis )
    'LBRACE',  # Left brace {
    'RBRACE',  # Right brace }
    'PLUS',   # Plus operator +
    'MINUS',   # Minus operator -
    'TIMES',   # Multiplication operator *
    'DIVIDE',  # Division operator /
    'EQUAL',   # Equal operator ==
    'NOTEQUAL',   # Not equal operator !=
    'LT',   # Less than operator <
    'GT',   # Greater than operator >
    'LE',   # Less than or equal operator <=
    'GE',  # Greater than or equal operator >=
    'COMMA',   # Comma ,
    'QUOTE',   # String delimiter "
    'COMMENT'  # Comment // or /* */
] + list(reserved.values())  # Reserved words are also tokens


# Token regex rules
t_ignore = ' \t'  # Ignore spaces and tabs
t_ASSIGN = r'='  # Assignment operator
t_SEMICOLON = r';'  # Statement terminator
t_LPAREN = r'\('  # Left parenthesis
t_RPAREN = r'\)'  # Right parenthesis
t_LBRACE = r'\{'  # Left brace
t_RBRACE = r'\}'  # Right brace
t_PLUS = r'\+'  # Plus operator
t_MINUS = r'-'  # Minus operator
t_TIMES = r'\*'  # Multiplication operator
t_DIVIDE = r'/'  # Division operator
t_EQUAL = r'=='  # Equal operator
t_NOTEQUAL = r'!='  # Not equal operator
t_LT = r'<'  # Less than operator
t_GT = r'>'  # Greater than operator
t_LE = r'<='  # Less than or equal operator
t_GE = r'>='  # Greater than or equal operator
t_COMMA = r','  # Comma
t_QUOTE = r'"'  # String delimiter


def t_NUMBER(t):  # Integer token
    r'\d+'
    t.value = int(t.value)
    return t
    

def t_IDENTIFIER(t):  # Identifier token (Doubles as string definition)
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')  # Check for reserved words
    return t


def t_COMMENT(t):  # Comment token
    r'//.*|/\*[\s\S]*?\*/'
    pass  # Ignore comments


def t_newline(t):  # Newline token
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):  # Error token
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)


lexer = lex.lex()
