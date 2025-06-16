"""
Definition of the nodes for the abstract syntax tree tree that will hold the script execution flow in a middle representation.

Classes:
    Node: Base abstract class for all nodes in the AST tree.
    Program: Represents the entire program.
    FunctionDef: Represents a function definition.
    FunctionCall: Represents a function call.
    IfStatement: Represents an if statement.
    WhileLoop: Represents a while loop.
    RepeatLoop: Represents a repeat loop.
    Assignment: Represents an assignment statement.
    Variable: Represents a variable.
    Literal: Represents a literal value.
    BinaryOp: Represents a binary operation.
    Action: Represents a robot action.
"""

from abc import ABC, abstractmethod


class Node(ABC):  # Abstract
    """
    Base class for all nodes in the AST tree.
    
    Methods: (Abstract methods)
        __init__(self): Initializes the node.
        __repr__(self): Provides a string representation of the node.

    Example:
        node = Node()

    Note: This is an abstract class and should not be instantiated directly. Use a specific node class instead.
    """
    @abstractmethod
    def __init__(self):
        """
        Initializes the node.
        """
        pass

    @abstractmethod
    def __repr__(self):
        """
        Provides a string representation of the node.
        """
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

    Example:
        program = Program([FunctionDef("main", [], [Assignment("x", Literal(10))])])
    """
    def __init__(self, statements):
        """
        Initializes the program with a list of statements.

        Args:
            statements (list): List of statements in the program.
        """
        self.statements = statements  # Statements of the program

    def __repr__(self):
        """
        Returns a string representation of the program.

        Returns:
            str: String representation of the program.
        """
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

    Example:
        func_def = FunctionDef("my_function", ["x", "y"], [Assignment("result", BinaryOp(Variable("x"), "+", Variable("y")))])
    """
    def __init__(self, name, params, body):
        """
        Initializes the function definition.

        Args:
            name (str): Function name.
            params (list): Parameters of the function (optional).
            body (list): Body of the function (list of statements).
        """
        self.name = name  # Function name
        self.param = params or []  # Parameters of the function (optional)
        self.body = body  # Body of the function (list of statements)

    def __repr__(self):
        """
        Returns a string representation of the function definition.

        Returns:
            str: String representation of the function definition.
        """
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

    Example:
        func_call = FunctionCall("my_function", [Variable("x"), Literal(10)])
    """
    def __init__(self, name, args=None):
        """
        Initializes the function call.

        Args:
            name (str): Function name.
            args (list): Arguments for the function call (optional).
        """
        self.name = name
        self.args = args or []

    def __repr__(self):
        """
        Returns a string representation of the function call.

        Returns:
            str: String representation of the function call.
        """
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

    Example:
        if_stmt = IfStatement(
            condition=BinaryOp(Variable("x"), ">", Literal(0)),
            true_branch=[Action("move", [Literal(10)])],
            false_branch=[Action("turn", [Literal(90)])]
        )
    """
    def __init__(self, condition, true_branch, false_branch=None):
        """
        Initializes the if statement.

        Args:
            condition (Node): Condition to evaluate.
            true_branch (list): Statements to execute if condition is true.
            false_branch (list): Statements to execute if condition is false (optional).
        """
        self.condition = condition  # Condition to evaluate
        self.true_branch = true_branch  # Statements to execute if condition is true
        self.false_branch = false_branch  # Statements to execute if condition is false (optional)

    def __repr__(self):
        """
        Returns a string representation of the if statement.

        Returns:
            str: String representation of the if statement.
        """
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

    Example:
        while_loop = WhileLoop(
            condition=BinaryOp(Variable("x"), "<", Literal(10)),
            body=[Action("move", [Literal(5)])]
        )
    """
    def __init__(self, condition, body):
        """
        Initializes the while loop.

        Args:
            condition (Node): Condition to evaluate.
            body (list): Statements to execute while condition is true.
        """
        self.condition = condition  # Condition to evaluate
        self.body = body  # Statements to execute while condition is true

    def __repr__(self):
        """
        Returns a string representation of the while loop.

        Returns:
            str: String representation of the while loop.
        """
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

    Example:
        repeat_loop = RepeatLoop(
            times=5,
            body=[Action("move", [Literal(10)])]
        )
    """
    def __init__(self, times, body):
        """
        Initializes the repeat loop.

        Args:
            times (int): Number of times to repeat.
            body (list): Statements to execute in each iteration.
        """
        self.times = times  # Number of times to repeat
        self.body = body  # Statements to execute in each iteration

    def __repr__(self):
        """
        Returns a string representation of the repeat loop.

        Returns:
            str: String representation of the repeat loop.
        """
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

    Example:
        assignment = Assignment("x", Literal(10))
    """
    def __init__(self, var_name, value):
        """
        Initializes the assignment statement.

        Args:
            var_name (str): Variable name.
            value (Node): Value to assign to the variable (can be a Variable, Literal, or BinaryOp).
        """
        self.var_name = var_name  # Variable name
        self.value = value  # Value to assign to the variable

    def __repr__(self):
        """
        Returns a string representation of the assignment statement.

        Returns:
            str: String representation of the assignment statement.
        """
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

    Example:
        variable = Variable("x")
    """
    def __init__(self, name):
        """
        Initializes the variable.

        Args:
            name (str): Variable name.
        """
        self.name = name  # Variable name

    def __repr__(self):
        """
        Returns a string representation of the variable.

        Returns:
            str: String representation of the variable.
        """
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

    Example:
        literal = Literal(10)
    """
    def __init__(self, value):
        """
        Initializes the literal value.

        Args:
            value (any): Literal value (Integer, String, etc...).
        """
        self.value = value  # Literal value (Integer, String, etc...)

    def __repr__(self):
        """
        Returns a string representation of the literal value.

        Returns:
            str: String representation of the literal value.
        """
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
        """
        Initializes the binary operation.

        Args:
            left (Node): Left operand (a Variable, Literal, or another BinaryOp).
            op (str): Operator (+, -, *, /).
            right (Node): Right operand (a Variable, Literal, or another BinaryOp).
        """
        self.left = left  # Left operand (a Variable, Literal, or another BinaryOp)
        self.op = op  # Operator (+, -, *, /)
        self.right = right  # Right operand (a Variable, Literal, or another BinaryOp)

    def __repr__(self):
        """
        Returns a string representation of the binary operation.

        Returns:
            str: String representation of the binary operation.
        """
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

    Example:
        action = Action("move", [])
    """
    def __init__(self, name, args=None):
        """
        Initializes the action.

        Args:
            name (str): Action name (see, move, turn, etc...).
            args (list): List of arguments for the action (optional).
        """
        self.name = name  # Action name (see, move, turn, etc...)
        self.args = args or []  # List of arguments (optional)

    def __repr__(self):
        """
        Returns a string representation of the action.

        Returns:
            str: String representation of the action.
        """
        args_repr = ", ".join([str(arg) for arg in self.args])
        return f"Action({self.name}, [{args_repr}])"
