import logging
import ply.yacc as yacc
from src.script.lexer import tokens
from src.script.lexer import reserved
from src.script.lexer import lexer
from src.script.ast_nodes import *


precedence = (
    ('right', 'ASSIGN'),            # Assignment (lowest precedence)
    ('left', 'EQUAL', 'NOTEQUAL', 'LT', 'GT', 'LE', 'GE'),  # Comparisons
    ('left', 'PLUS', 'MINUS'),      # Addition/subtraction
    ('left', 'TIMES', 'DIVIDE'),    # Multiplication/division (highest precedence)
)


def p_program(p):
    '''program : statement_list
               | '''
    if len(p) == 2:  # If there are statements
        p[0] = Program(p[1])  # Create a Program node with the statement list
    else:  # If there are no statements
        p[0] = Program([])  # Create an empty Program node


def p_statement_list(p):
    '''statement_list : statement
                      | statement_list statement'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []  # Single statement
    else:
        p[0] = p[1] + ([p[2]] if p[2] is not None else [])  # Concatenate two statement lists


def p_statement(p):
    '''statement : assignment SEMICOLON
                 | action SEMICOLON
                 | function_call SEMICOLON
                 | loop
                 | condition
                 | function_def
                 | COMMENT'''
    if len(p) == 2 and p.slice[1].type == 'COMMENT':
        p[0] = None
    else:
        p[0] = p[1]


def p_assignment(p):
    '''assignment : IDENTIFIER ASSIGN expression'''
    if p[1] in reserved:
        raise SyntaxError(
            f"At line {p.lineno(1)}: Cannot use reserved word '{p[1]}' as variable name. "
            f"Please choose a different name for your variable."
        )
    p[0] = Assignment(p[1], p[3])


def p_loop(p):
    '''loop : REPEAT NUMBER LBRACE statement_list RBRACE
            | WHILE LPAREN condition_expr RPAREN LBRACE statement_list RBRACE'''
    if len(p) == 6:  # Repeat loop
        p[0] = RepeatLoop(Literal(p[2]), p[4])
    else:  # While loop
        p[0] = WhileLoop(p[3], p[6])


def p_condition(p):
    '''condition : IF LPAREN condition_expr RPAREN LBRACE statement_list RBRACE
                 | IF LPAREN condition_expr RPAREN LBRACE statement_list RBRACE ELSE LBRACE statement_list RBRACE'''
    if len(p) == 8:  # If without else
        p[0] = IfStatement(p[3], p[6], None)
    else:  # If with else
        p[0] = IfStatement(p[3], p[6], p[10])


def p_condition_expr(p):
    '''condition_expr : expression comparison_operator expression'''
    p[0] = BinaryOp(p[1], p[2], p[3])


def p_comparison_operator(p):
    '''comparison_operator : EQUAL
                            | NOTEQUAL
                            | LT
                            | GT
                            | LE
                            | GE'''
    p[0] = p[1]  # Pass through as string


def p_expression(p):
    '''expression : IDENTIFIER
                  | NUMBER
                  | function_call
                  | arithmetic_expr
                  | object_type
                  | action'''
    match p.slice[1].type:
        case 'IDENTIFIER':
            p[0] = Variable(p[1])
        case 'NUMBER':
            p[0] = Literal(p[1])
        case 'function_call':
            p[0] = p[1]
        case 'arithmetic_expr':
            p[0] = p[1]
        case 'object_type':
            p[0] = p[1]
        case 'action':
            p[0] = p[1]
        case _:
            raise SyntaxError(f"Unexpected token: {p.slice[1].type}")


def p_arithmetic_expr(p):
    '''arithmetic_expr : expression arithmetic_operator expression'''
    p[0] = BinaryOp(p[1], p[2], p[3])


def p_arithmetic_operator(p):
    '''arithmetic_operator : PLUS
                            | MINUS
                            | TIMES
                            | DIVIDE'''
    p[0] = p[1]


def p_function_def(p):
    '''function_def : FUNC IDENTIFIER LPAREN RPAREN LBRACE statement_list RBRACE
                    | FUNC IDENTIFIER LPAREN parameter_list RPAREN LBRACE statement_list RBRACE'''
    if p[2] in reserved:
        raise SyntaxError(
            f"At line {p.lineno(2)}: Cannot use reserved word '{p[2]}' as function name. "
            f"Please choose a different name for your function."
        )
    if len(p) == 9:  # With parameters
        p[0] = FunctionDef(p[2], p[4], p[7])
    else:  # Without parameters
        p[0] = FunctionDef(p[2], [], p[6])
        

def p_parameter_list(p):
    '''parameter_list : IDENTIFIER COMMA parameter_list
                      | IDENTIFIER'''
    if len(p) == 4:  # Recursive case
        p[0] = [p[1]] + p[3]
    else:  # Base case
        p[0] = [p[1]]


def p_userfunc(p):
    '''userfunc : IDENTIFIER'''
    if p[1] in reserved:
        raise SyntaxError(f"Expected user-defined function, got reserved keyword: {p[1]}")
    p[0] = p[1]


def p_function_call(p):
    '''function_call : userfunc LPAREN argument_list RPAREN
                     | userfunc LPAREN RPAREN'''
    if len(p) == 5:
        p[0] = FunctionCall(p[1], p[3])
    else:
        p[0] = FunctionCall(p[1], [])
        

def p_argument_list(p):
    '''argument_list : expression COMMA argument_list
                     | expression'''
    if len(p) == 4:  # Recursive case
        p[0] = [p[1]] + p[3]
    else:  # Base case
        p[0] = [p[1]]


def p_action(p):
    '''action : MOVE LPAREN RPAREN
              | TURN_RIGHT LPAREN RPAREN
              | TURN_LEFT LPAREN RPAREN
              | PICKUP LPAREN RPAREN
              | DROP LPAREN RPAREN
              | SEE LPAREN RPAREN
              | READ LPAREN RPAREN
              | WRITE LPAREN expression RPAREN
              | WAIT LPAREN RPAREN'''
    action_type = p.slice[1].type
    if len(p) == 5:  # Action with an argument
        match action_type:
            case 'WRITE':
                p[0] = Action("write", [p[3]])
            case _:
                raise SyntaxError(f"Unexpected action with argument: {action_type}")
    else:  # Actions without arguments
        match action_type:
            case 'MOVE':
                p[0] = Action("move", [])
            case 'TURN_RIGHT':
                p[0] = Action("turn", ["right"])  # level.turn requires both the entity and the direction
            case 'TURN_LEFT':
                p[0] = Action("turn", ["left"])
            case 'PICKUP':
                p[0] = Action("pickup", [])
            case 'DROP':
                p[0] = Action("drop", [])
            case 'SEE':
                p[0] = Action("see", [])
            case 'READ':
                p[0] = Action("read", [])
            case 'WAIT':
                p[0] = Action("wait", [])
            case _:
                raise SyntaxError(f"Unexpected action without argument: {action_type}")
            

def p_object_type(p):  # A string definition
    '''object_type : STRING'''
    p[0] = Literal(p[1])


def p_error(p):
    """
    Robust generic error handler using match-case.
    """
    if p is None:
        raise SyntaxError(
            "Unexpected end of input. Did you forget to close a block (e.g., with '}' or ')') or miss a semicolon ';'?"
        )

    token_type = p.type
    value = p.value
    line = p.lineno
    col_info = f" (line {line})"

    match token_type:
        case "ELSE":
            raise SyntaxError(f"Unexpected 'else'{col_info}. Is there a missing 'if' block above?")
        case "RBRACE":
            raise SyntaxError(f"Unmatched '}}'{col_info}. Did you forget to open a block with '{{'?")
        case "LBRACE":
            raise SyntaxError(f"Unexpected '{{'{col_info}. Blocks should follow control statements like 'if' or 'while'.")
        case "RPAREN":
            raise SyntaxError(f"Unmatched ')'{col_info}. Check for missing or misplaced '('.")
        case "LPAREN":
            raise SyntaxError(f"Unexpected '(' {col_info}. Did you forget a function or action name before it?")
        case "SEMICOLON":
            raise SyntaxError(f"Unexpected ';'{col_info}. You might have an extra semicolon or empty statement.")
        case "IDENTIFIER":
            raise SyntaxError(f"Unexpected identifier '{value}'{col_info}. Did you forget a keyword or a semicolon before it?")
        case "NUMBER":
            raise SyntaxError(f"Unexpected number '{value}'{col_info}. Did you forget to use it in an expression?")
        case "COMMENT":
            raise SyntaxError(f"Unexpected comment '{value}'{col_info}. Comments should not interrupt code flow.")
        case "COMMA":
            raise SyntaxError(f"Unexpected ','{col_info}. Are you missing an argument or value?")
        case op if op in {"PLUS", "MINUS", "TIMES", "DIVIDE", "LT", "GT", "LE", "GE", "EQUAL", "NOTEQUAL"}:
            raise SyntaxError(f"Unexpected operator '{value}'{col_info}. Are you missing an operand or expression?")
        case kw if kw in {"MOVE", "TURN_LEFT", "TURN_RIGHT", "PICKUP", "DROP", "WAIT", "SEE", "READ", "WRITE"}:
            raise SyntaxError(f"Unexpected action '{value}'{col_info}. Did you forget to add parentheses? Try '{value.lower()}();'")
        case ctrl if ctrl in {"IF", "WHILE", "RETURN"}:
            raise SyntaxError(f"Unexpected keyword '{value}'{col_info}. Is it in the wrong place, or missing a block or condition?")
        case kw if kw in reserved.values():
            raise SyntaxError(f"Unexpected keyword '{value}'{col_info}. Is it used in the wrong place?")
        case _:
            raise SyntaxError(f"Unexpected token '{value}' of type '{token_type}'{col_info}. Refer to the syntax help for guidance.")


parser = yacc.yacc(debug=False, write_tables=False)


def parse_code(source_code):
    """
    Parses the given source code into an AST.
    Returns the Program node containing all statement_list.
    """
    lexer.lineno = 1
    lexer.input(source_code)  # Initialize the lexer with the source code

    try:
        result = parser.parse(source_code, tracking=True, lexer=lexer)
        if isinstance(result, Program):
            return result
        elif result is None:
            return Program([])
        else:
            return Program([result])
    except SyntaxError as e:
        logging.error(f"Syntax error: {e}")
        raise e