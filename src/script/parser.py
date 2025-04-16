import logging
import ply.yacc as yacc
from src.script.lexer import tokens
from src.script.lexer import reserved
from src.script.ats_nodes import *


class SyntaxErrorException(Exception):
    def __init__(self, message, lineno=None, position=None, token=None):
        self.message = message
        self.lineno = lineno
        self.position = position
        self.token = token
        self.user_friendly = self._make_user_friendly()
        super().__init__(self.message)


    def _make_user_friendly(self):
        """Convert technical error messages to user-friendly ones"""
        user_friendly_message = None
        if "Syntax error at" in self.message:
            match self.token:
                case 'SEMICOLON' | ';':
                    user_friendly_message = f"Missing semicolon at line {self.lineno}"
                case 'RBRACE' | '}':
                    user_friendly_message = f"Missing closing brace '}}' at line {self.lineno}"
                case 'RPAREN' | ')':
                    user_friendly_message = f"Missing closing parenthesis ')' at line {self.lineno}"
                case 'LBRACE' | '{':
                    user_friendly_message = f"Missing opening brace '{{' at line {self.lineno}"
                case 'LPAREN' | '(':
                    user_friendly_message = f"Missing opening parenthesis '(' at line {self.lineno}"
                case _:
                    user_friendly_message = f"Unexpected '{self.token}' at line {self.lineno}"
        elif "Expected user-defined function" in self.message:
            user_friendly_message = f"Cannot use '{self.token}' as a function name (it's a reserved word)"
        elif "Unexpected action" in self.message:
            user_friendly_message = f"Invalid action syntax at line {self.lineno}"
        elif "invalid syntax" in self.message.lower():
            return f"Invalid syntax at line {self.lineno}"
        elif "unexpected indent" in self.message.lower():
            return f"Unexpected indentation at line {self.lineno}"
        elif "expected an indented block" in self.message.lower():
            return f"Missing code block after control statement at line {self.lineno}"
        else:
            user_friendly_message = f"Syntax error at line {self.lineno}: {self.message}"
        return user_friendly_message


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
                 | loop
                 | condition
                 | function_def
                 | function_call SEMICOLON
                 | COMMENT'''
    if p.slice[1].type == 'COMMENT':
        p[0] = None  # Skip comments
    else:
        p[0] = p[1]


def p_assignment(p):
    '''assignment : IDENTIFIER ASSIGN expression'''
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
    if len(p) == 9:  # With parameters
        p[0] = FunctionDef(p[2], p[4], p[7])  # Pass parameters to the function definition
    else:  # Without parameters
        p[0] = FunctionDef(p[2], [], p[6])  # Pass empty list for parameters
        

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
            

def p_object_type(p):  # A string definition, but called like this since it's only used to identify the object type when calling see()
    '''object_type : QUOTE IDENTIFIER QUOTE'''
    p[0] = Literal(p[2])


def p_error(p):
    if p:
        raise SyntaxErrorException(
            f"Syntax error at '{p.value}'",
            lineno=p.lineno,
            position=p.lexpos,
            token=p.value
        )
    else:
        raise SyntaxErrorException("Syntax error at end of file - possibly missing closing brace or parenthesis")


# Build the parser
parser = yacc.yacc(debug=True, write_tables=False)


def parse_code(source_code):
    """
    Parses the given source code into an AST.
    Returns the Program node containing all statement_list.
    Raises SyntaxErrorException if syntax errors are found.
    """
    try:
        result = parser.parse(source_code)
        if isinstance(result, Program):
            return result
        elif result is None:
            return Program([])
        else:
            return Program([result] if result is not None else [])
    except SyntaxErrorException as e:
        # Enhance the error message with line context if available
        if e.lineno and source_code:
            lines = source_code.split('\n')
            if 0 < e.lineno <= len(lines):
                context = lines[e.lineno - 1].strip()
                e.user_friendly += f"\nNear: '{context}'"
        raise