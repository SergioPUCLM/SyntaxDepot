"""Coroutine Interpreter class"""
from src.script.ast_nodes import *


class CoroutineInterpreter:
    """
    Coroutine Interpreter for executing a script in a coroutine-like manner.
    This interpreter is responsible for executing the script using a stack of environments
    to manage local variables and function calls.
    Attributes:
        level (Level): The level where actions should be executed.
        entity (Entity): The entity (or robot) that will perform the actions.
        env_stack (list): Stack of environments for local variables and function calls.
    Methods:
        __init__(self, level, entity): Initializes the CoroutineInterpreter.
        push_env(): Pushes a new environment onto the stack.
        pop_env(): Pops the current environment from the stack.
        current_env(): Gets the current environment (top of the stack).
        set_var(name, value): Sets a variable in the current environment.
        get_var(name): Gets a variable from the current environment.
        find_function(name, program_node): Finds a function declaration by its name.
        run(program_node): Executes the program node.
        _eval(node): Evaluates the AST node and dispatches to appropriate method.
        _eval_*(node): Evaluates specific types of nodes (e.g., Program, FunctionDeclaration, Assignment, etc.).
    """

    def __init__(self, level, entity):
        """
        Initialize the CoroutineInterpreter.
        This interpreter is responsible for executing the script
        in a coroutine-like manner.
        It uses a stack of environments to manage local variables
        and function calls.

        Args:
            level (Level): The level where actions should be executed.
            entity (Entity): The entity (or robot) that will perform the actions
        """
        self.level = level  # Level where actions should be executed
        self.entity = entity  # Robot that will perform the execution
        self.env_stack = [{}]  # Scope stack: one dict per frame


    def push_env(self):
        """
        Push a new environment onto the stack.
        This creates a new scope for local variables.
        """
        self.env_stack.append({})


    def pop_env(self):
        """
        Pop the current environment from the stack.
        This removes the current scope for local variables.
        """
        self.env_stack.pop()


    def current_env(self):
        """
        Get the current environment (top of the stack).
        This is where local variables are stored.
        """
        return self.env_stack[-1]


    def set_var(self, name, value):
        """
        Set a variable in the current environment.
        If the variable is not found in the current environment,
        it will be created.
        """
        self.current_env()[name] = value


    def get_var(self, name):
        """
        Get a variable from the current environment.
        If the variable is not found in the current environment,
        it will search in the parent environments.

        Args:
            name (str): The name of the variable to retrieve.

        Raises:
            RuntimeError: If the variable is not found in any environment.

        Returns:
            The value of the variable.
        """
        for env in reversed(self.env_stack):
            if name in env:
                return env[name]
        raise RuntimeError(f"Undefined variable: {name}")


    def find_function(self, name, program_node):
        """
        Find a function declaration by its name in the program node.
        This searches through the program node's statements to find
        the function with the given name.

        Args:
            name (str): The name of the function to find.
            program_node (Program): The program node containing function declarations.

        Returns:
            FunctionDeclaration: The function declaration node if found.
        """
        for stmt in program_node.statements:
            if isinstance(stmt, FunctionDeclaration) and stmt.name == name:
                return stmt
        return None


    def run(self, program_node):
        """
        Execute the program node.
        This method is the entry point for executing the script.
        It initializes the environment and starts the execution.

        Args:
            program_node (Program): The program node to execute.

        Returns:
            Generator: A generator that yields the results of the execution.
        """
        return self._eval(program_node)


    def _eval(self, node):
        """
        Evaluate the AST node.
        This method dispatches the evaluation to the appropriate
        method based on the type of node.

        Args:
            node (Node): The AST node to evaluate.

        Yields:
            The result of the evaluation.
        """

        if node is None:
            raise RuntimeError("Tried to evaluate a None node. Possible missing parser return?")

        # Handle literal values
        if isinstance(node, Literal):
            return node.value

        # Handle simple values (In case something breaks, but it should never reach this)
        if isinstance(node, (int, str)):
            return node

        # Handle variables
        if isinstance(node, Variable):
            return self._eval_Variable(node)

        # Handle function definitions
        if isinstance(node, FunctionDef):
            return self._eval_FunctionDef(node)


        method = getattr(self, f"_eval_{type(node).__name__}", None)
        if method:
            gen = method(node)  # Call the method to get a generator
            if isinstance(node, (Variable, BinaryOp, FunctionDef)):
                result = None
                try:
                    while True:
                        # Advance the generator and get yielded values
                        yielded = gen.send(result)
                        # If we get a generator, run it to completion
                        if hasattr(yielded, '__iter__'):
                            result = yield from yielded
                        else:
                            result = yielded
                except StopIteration as e:
                    return e.value if e.value is not None else result
            else:
                # For statements, just yield from normally
                return (yield from gen)
        else:
            raise NotImplementedError(f"No visitor for node type {type(node).__name__}")

        
    def _eval_Program(self, node):
        """
        Evaluate the program node.
        This method executes all the statements in the program.

        Args:
            node (Program): The program node to evaluate.

        Yields:
            The results of the evaluation of each statement.
        """
    
        # First pass: register all functions
        for stmt in node.statements:
            if isinstance(stmt, FunctionDef):
                self._eval_FunctionDef(stmt)
        
        # Second pass: execute other statements
        for stmt in node.statements:
            if not isinstance(stmt, FunctionDef):
                yield from self._eval(stmt)


    def _eval_FunctionDef(self, node):
        """
        Evaluate a function declaration node.
        This method stores the function in the current environment.

        Args:
            node (FunctionDeclaration): The function declaration node to evaluate.

        Yields:
            None
        """
        self.set_var(node.name, {
            'params': node.param,
            'body': node.body
        })
        return None  # No value to yield, just register the function


    def _eval_Assignment(self, node):
        """
        Evaluate an assignment node.
        This method evaluates the expression on the right-hand side
        and assigns its value to the variable on the left-hand side.

        Args:
            node (Assignment): The assignment node to evaluate.

        Yields:
            The value assigned to the variable.
        """
        value = yield from self._eval(node.value)
        self.set_var(node.var_name, value)


    def _eval_Identifier(self, node):
        """
        Evaluate an identifier node.
        This method retrieves the value of the variable
        from the current environment.

        Args:
            node (Identifier): The identifier node to evaluate.

        Returns:
            The value of the variable.
        """
        return self.get_var(node.name)


    def _eval_Literal(self, node):
        """
        Evaluate a literal node.
        This method returns the literal value.
        This is used for numbers and strings.

        Args:
            node (Literal): The literal node to evaluate.

        Returns:
            The literal value.
        """
        return node.value  # Return the literal value  (Numbers and Strings)


    def _eval_BinaryOp(self, node):
        """
        Evaluate a binary operation node.
        This method evaluates the left and right operands
        and applies the operator to them.

        Args:
            node (BinaryOperation): The binary operation node to evaluate.

        Yields:
            The result of the binary operation.
        """
        left = yield from self._eval(node.left)
        right = yield from self._eval(node.right)

        match node.op:
            case '+':
                return left + right
            case '-':
                return left - right
            case '*':
                return left * right
            case '/':
                return left // right if right != 0 else 0  # Avoid division by zero
            case '==':
                return int(left == right)
            case '!=':
                return int(left != right)
            case '<':
                return int(left < right)
            case '>':
                return int(left > right)
            case '<=':
                return int(left <= right)
            case '>=':
                return int(left >= right)
            case _:
                raise RuntimeError(f"Unknown operator: {node.op}")


    def _eval_Action(self, node):
        """
        Evaluate an action node.
        This method maps the action name to the corresponding
        method in the level and executes it.

        Args:
            node (Action): The action node to evaluate.

        Yields:
            The result of the action execution.
        """
        action_map = {
        "move": lambda args: self.level.move(self.entity),
        "turn": lambda args: self.level.turn(self.entity, *args),
        "see": lambda args: self.level.see(self.entity),
        "pickup": lambda args: self.level.pickup(self.entity),
        "drop": lambda args: self.level.drop(self.entity),
        "read": lambda args: self.level.read(self.entity),
        "write": lambda args: self.level.write(self.entity, *args),
        "wait": lambda args: self.level.wait(self.entity)
        }

        evaluated_args = []
        for arg in node.args:
            if isinstance(arg, Node):
                evaluated_args.append((yield from self._eval(arg)))
            else:
                evaluated_args.append(arg)

        if node.name not in action_map:
            raise RuntimeError(f"Unknown action: {node.name}")

        result = action_map[node.name](evaluated_args)
        
        # Don't yield on see()
        if node.name != "see":
            yield  # Pause after action
        return result


    def _eval_IfStatement(self, node):
        """
        Evaluate an if statement node.
        This method evaluates the condition and executes the
        true body if the condition is true, or the false body
        if the condition is false.

        Args:
            node (IfStatement): The if statement node to evaluate.

        Yields:
            The results of the evaluation of the true or false body.
        """
        condition = yield from self._eval(node.condition)
        if condition != 0:
            for stmt in node.true_branch:
                yield from self._eval(stmt)
        elif node.false_branch:
            for stmt in node.false_branch:
                yield from self._eval(stmt)


    def _eval_WhileLoop(self, node):
        """
        Evaluate a while statement node.
        This method evaluates the condition and executes the
        body while the condition is true.

        Args:
            node (WhileStatement): The while statement node to evaluate.

        Yields:
            The results of the evaluation of the body.
        """
        while True:
            condition = yield from self._eval(node.condition)
            if condition == 0:
                break
            for stmt in node.body:
                yield from self._eval(stmt)


    def _eval_RepeatLoop(self, node):
        """
        Evaluate a repeat loop node.
        This method evaluates the repeat count and executes the
        body the specified number of times.

        Args:
            node (RepeatLoop): The repeat loop node to evaluate.
        Yields:
            The results of the evaluation of the body.
        """
        times = yield from self._eval(node.times)

        if not isinstance(times, int):
            raise RuntimeError(f"Repeat count must be an int, got {type(times)}")

        # Ensure body is a list
        body = node.body if isinstance(node.body, list) else [node.body]

        try:
            for _ in range(times):
                for stmt in body:
                    yield from self._eval(stmt)
        except Exception as e:
            raise RuntimeError(f"Repeat loop failed: {e}")

    
    def _eval_FunctionCall(self, node):
        """
        Evaluate a function call node.
        This method retrieves the function from the environment,
        evaluates the arguments, and executes the function body.

        Args:
            node (FunctionCall): The function call node to evaluate.

        Yields:
            The results of the function execution.
        """
    
        # Get the function definition
        try:
            func_def = self.get_var(node.name)
        except RuntimeError:
            raise RuntimeError(f"Function '{node.name}' is not defined")
        
        if not isinstance(func_def, dict) or 'body' not in func_def:
            raise RuntimeError(f"'{node.name}' is not a function")
        
        # Evaluate arguments
        evaluated_args = []
        for arg in node.args:
            arg_value = yield from self._eval(arg)
            evaluated_args.append(arg_value)
        
        # Parameter validation
        if len(evaluated_args) != len(func_def['params']):
            raise RuntimeError(f"Function {node.name} expects {len(func_def['params'])} arguments, got {len(evaluated_args)}")
        
        # Create new scope
        self.push_env()
        
        try:
            # Bind parameters
            for param, arg in zip(func_def['params'], evaluated_args):
                self.set_var(param, arg)
            
            # Execute function body (ensure it's a list)
            body = func_def['body'] if isinstance(func_def['body'], list) else [func_def['body']]
            for stmt in body:
                yield from self._eval(stmt)
        finally:
            self.pop_env()


    def _eval_ObjectType(self, node):
        """
        Evaluate an object type node.
        This method returns the name of the object type.

        Args:
            node (ObjectType): The object type node to evaluate.

        Yields:
            The name of the object type.
        """
        return node.name  # it's just a string identifier


    def _eval_Variable(self, node):#MODIFIED
        """
        Evaluate a variable node by looking up its value in the current environment.
        This method retrieves the value of the variable from the environment.
        
        Args:
            node (Variable): The variable node to evaluate.
            
        Yields:
            The value of the variable.
        """
        value = self.get_var(node.name)
        return value # CHANGED FROM YIELD TO RETURN
