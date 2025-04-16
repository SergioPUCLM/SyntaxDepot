"""Definition of the nodes for the ATS tree that will hold the script execution flow in a middle representation."""
from abc import ABC, abstractmethod


class Node(ABC):  # Abstract
    """
    Base class for all nodes in the ATS tree.
    """
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass


class Program(Node):
    """
    Represents the entire program.
    Contains a list of statements.

    Attributes:
        statements (list): List of statements in the program.
    Methods:
        __init__(self, statements): Initializes the program with a list of statements.
        __repr__(self): Returns a string representation of the program.
    """
    def __init__(self, statements):
        self.statements = statements  # Statements of the program

    def __repr__(self):
        statements_repr = "\n".join([f"  {stmt}" for stmt in self.statements])
        return f"Program(\n{statements_repr}\n)"


class FunctionDef(Node):
    """
    Represents a function definition.
    Contains the function name, parameters, and body.

    Attributes:
        name (str): Function name.
        param (list): Parameters of the function (optional).
        body (list): Body of the function (list of statements).

    Methods:
        __init__(self, name, params, body): Initializes the function definition.
        __repr__(self): Returns a string representation of the function definition.
    """
    def __init__(self, name, params, body):
        self.name = name  # Function name
        self.param = params or []  # Parameters of the function (optional)
        self.body = body  # Body of the function (list of statements)

    def __repr__(self):
        params_repr = ", ".join([str(param) for param in self.param])
        body_repr = "\n".join([f"  {stmt}" for stmt in self.body])
        return f"FunctionDef({self.name}, [{params_repr}],\n{body_repr}\n)"


class FunctionCall(Node):
    """
    Represents a function call.
    Contains the function name and its arguments.

    Attributes:
        name (str): Function name.

    Methods:
        __init__(self, name, args): Initializes the function call.
        __repr__(self): Returns a string representation of the function call.
    """
    def __init__(self, name, args=None):
        self.name = name
        self.args = args or []

    def __repr__(self):
        args_repr = ", ".join([str(arg) for arg in self.args])
        return f"FunctionCall({self.name}, [{args_repr}])"


class IfStatement(Node):
    """
    Represents an if statement.
    Contains the condition, true branch, and optional false branch.

    Attributes:
        condition (Node): Condition to evaluate.
        true_branch (list): Statements to execute if condition is true.
        false_branch (list): Statements to execute if condition is false (optional).
    Methods:
        __init__(self, condition, true_branch, false_branch=None): Initializes the if statement.
        __repr__(self): Returns a string representation of the if statement.
    """
    def __init__(self, condition, true_branch, false_branch=None):
        self.condition = condition  # Condition to evaluate
        self.true_branch = true_branch  # Statements to execute if condition is true
        self.false_branch = false_branch  # Statements to execute if condition is false (optional)

    def __repr__(self):
        true_branch_repr = "\n".join([f"  {stmt}" for stmt in self.true_branch])
        false_branch_repr = "\n".join([f"  {stmt}" for stmt in self.false_branch]) if self.false_branch else ""
        return f"If({self.condition},\n{true_branch_repr}\n, Else:\n{false_branch_repr}\n)"


class WhileLoop(Node):
    """
    Represents a while loop.
    Contains the loop condition and body.

    Attributes:
        condition (Node): Condition to evaluate.
        body (list): Statements to execute while condition is true.

    Methods:
        __init__(self, condition, body): Initializes the while loop.
        __repr__(self): Returns a string representation of the while loop.
    """
    def __init__(self, condition, body):
        self.condition = condition  # Condition to evaluate
        self.body = body  # Statements to execute while condition is true

    def __repr__(self):
        body_repr = "\n".join([f"  {stmt}" for stmt in self.body])
        return f"While({self.condition},\n{body_repr}\n)"


class RepeatLoop(Node):
    """
    Represents a repeat loop.
    Contains the number of repetitions and the body.

    Attributes:
        times (int): Number of times to repeat.
        body (list): Statements to execute in each iteration.

    Methods:
        __init__(self, times, body): Initializes the repeat loop.
        __repr__(self): Returns a string representation of the repeat loop.
    """
    def __init__(self, times, body):
        self.times = times  # Number of times to repeat
        self.body = body  # Statements to execute in each iteration

    def __repr__(self):
        body_repr = "\n".join([f"  {stmt}" for stmt in self.body])
        return f"Repeat({self.times},\n{body_repr}\n)"


class Assignment(Node):
    """
    Represents an assignment statement.
    Contains the variable name and the value to assign.

    Attributes:
        var_name (str): Variable name.
        value (Node): Value to assign to the variable.

    Methods:
        __init__(self, var_name, value): Initializes the assignment statement.
        __repr__(self): Returns a string representation of the assignment statement.
    """
    def __init__(self, var_name, value):
        self.var_name = var_name  # Variable name
        self.value = value  # Value to assign to the variable

    def __repr__(self):
        return f"Assign({self.var_name}, {self.value})"


class Variable(Node):
    """
    Represents a variable.
    Contains the variable name.

    Attributes:
        name (str): Variable name.

    Methods:    
        __init__(self, name): Initializes the variable.
        __repr__(self): Returns a string representation of the variable.
    """
    def __init__(self, name):
        self.name = name  # Variable name

    def __repr__(self):
        return f"Variable({self.name})"


class Literal(Node):
    """
    Represents a literal value.
    Contains the value.
    Attributes:
        value (any): Literal value (Integer, String, etc...).

    Methods:
        __init__(self, value): Initializes the literal value.
        __repr__(self): Returns a string representation of the literal value.
    """
    def __init__(self, value):
        self.value = value  # Literal value (Integer, String, etc...)

    def __repr__(self):
        return f"Literal({self.value})"


class BinaryOp(Node):
    """
    Represents a binary operation.
    Contains the left operand, operator, and right operand.

    Attributes:
        left (Node): Left operand (a Variable, Literal, or another BinaryOp).
        op (str): Operator (+, -, *, /).
        right (Node): Right operand (a Variable, Literal, or another BinaryOp).

    Methods:
        __init__(self, left, op, right): Initializes the binary operation.
        __repr__(self): Returns a string representation of the binary operation.
    """
    def __init__(self, left, op, right):
        self.left = left  # Left operand (a Variable, Literal, or another BinaryOp)
        self.op = op  # Operator (+, -, *, /)
        self.right = right  # Right operand (a Variable, Literal, or another BinaryOp)

    def __repr__(self):
        return f"BinaryOp({self.left}, {self.op}, {self.right})"


class Action(Node):
    """
    Represents a robot action.
    Contains the action name and its arguments.

    Attributes:
        name (str): Action name (see, move, turn, etc...).
        args (list): List of arguments (optional).

    Methods:
        __init__(self, name, args=None): Initializes the action.
        __repr__(self): Returns a string representation of the action.
    """
    def __init__(self, name, args=None):
        self.name = name  # Action name (see, move, turn, etc...)
        self.args = args or []  # List of arguments (optional)

    def __repr__(self):
        args_repr = ", ".join([str(arg) for arg in self.args])
        return f"Action({self.name}, [{args_repr}])"
