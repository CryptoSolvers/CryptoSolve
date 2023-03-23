"""
This module is responsible for creating
terms out of strings, given a set of
known terms.
"""
from typing import Optional, Union, Set, List
from .term import Variable, Constant, Function, Term

__all__ = ['Parser']

class Parser:
    """
    A string parser library.

    Given a signature, the parser can then take a string
    that represents a term and create the term using the
    algebra library.

    Examples
    --------
    >>> from symcollab.algebra import *
    >>> f = Function("f", 2)
    >>> x = Variable("x")
    >>> p = Parser()
    >>> p.add(f)
    >>> p.add(x)
    >>> p.parse("f(x,x)")
    f(x, x)
    """
    def __init__(self):
        self.variables: Set[Variable] = set()
        self.constants: Set[Constant] = set()
        self.functions: Set[Function] = set()

    def add(self, term: Union[Variable, Constant, Function]):
        """Adds a term to the parser."""
        if isinstance(term, Variable):
            if self._find_constant(term.symbol) is not None:
                raise ValueError("Symbol is already defined as a constant in the Parser")
            if self._find_function(term.symbol) is not None:
                raise ValueError("Symbol is already defined as a function in the Parser")
            self.variables.add(term)
        elif isinstance(term, Constant):
            if self._find_variable(term.symbol) is not None:
                raise ValueError("Symbol is already defined as a variable in the Parser")
            if self._find_function(term.symbol) is not None:
                raise ValueError("Symbol is already defined as a function in the Parser")
            self.constants.add(term)
        elif isinstance(term, Function):
            if self._find_constant(term.symbol) is not None:
                raise ValueError("Symbol is already defined as a constant in the Parser")
            if self._find_variable(term.symbol) is not None:
                raise ValueError("Symbol is already defined as a variable in the Parser")
            self.functions.add(term)
        else:
            raise ValueError("Argument to Parser.add must be a Variable, Constant, or Function")

    def remove(self, term: Union[Variable, Constant, Function]):
        """Remove a term from the parser."""
        if isinstance(term, Variable):
            self.variables -= {term}
        elif isinstance(term, Constant):
            self.constants -= {term}
        elif isinstance(term, Function):
            self.functions -= {term}

    def parse(self, x: str) -> Union[Term, Function]:
        """Attempt to parse a string given the parser's existing signature."""
        # First remove all whitespace since it's irrelevant
        x = x.replace(' ', '')
        start_i = x.find("(")
        if start_i != -1:
            end_i = self._find_last_char(")", x)
            if end_i == -1:
                raise ValueError("Parenthesis misbalance")

            # We have a function!
            function_name = x[:start_i]
            function_handle = self._find_function(function_name)
            if function_handle is None:
                raise ValueError("Function " + function_name + " is not defined in the Parser")

            argument_strings = self._parse_arguments(x[(start_i + 1):(end_i - 1)])

            if len(argument_strings) != function_handle.arity:
                raise ValueError("Arity Mismatch: Parsed String: " + str(len(argument_strings)) +
                    ", Function " + function_handle.symbol + ": " + str(function_handle.arity))

            args = [self.parse(arg_string) for arg_string in argument_strings]
            return function_handle(*args)
        else:
            x_var = self._find_variable(x)
            if x_var is not None:
                return x_var
            x_constant = self._find_constant(x)
            if x_constant is not None:
                return x_constant
            x_function = self._find_function(x)
            if x_function is not None:
                return x_function
            # If none of the above matched return an error
            raise ValueError("Symbol " + x + " is undefined in the Parser")

    def _find(self, x: str, container: List[Union[Function, Constant, Variable]]):
        for c in container:
            if x == c.symbol:
                return c
        return None

    def _find_function(self, x: str) -> Optional[Function]:
        return self._find(x, self.functions)

    def _find_constant(self, x: str) -> Optional[Constant]:
        return self._find(x, self.constants)

    def _find_variable(self, x: str) -> Optional[Variable]:
        return self._find(x, self.variables)

    def _find_last_char(self, needle: str, haystack: str) -> int:
        for i, c in enumerate(reversed(haystack)):
            if c == needle:
                return len(haystack) - i
        return -1

    # Splits the arguments up to a list of arguments
    def _parse_arguments(self, arguments_string: str) -> List[str]:
        args: List[str] = []
        start_i = 0
        num_parentheses = 0
        for i, c in enumerate(arguments_string):
            # If we saw an opening parenthesis,
            # we need to ignore input until the end parenthesis is matched.
            if num_parentheses > 0:
                if c == ")":
                    num_parentheses -= 1
                elif c == "(":
                    num_parentheses += 1
            else:
                if c == ",":
                    args.append(arguments_string[start_i:i])
                    start_i = i + 1
                elif c == "(":
                    num_parentheses += 1

        if num_parentheses > 0:
            raise ValueError("Parenthesis Mismatch")

        # Add last argument
        args.append(arguments_string[start_i:])
        return args
