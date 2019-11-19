import sympy # type: ignore
from .term import *

@overload
def termToSympy(term : Constant) -> sympy.Symbol:
    """Converts a constant to a sympy symbol"""
@overload
def termToSympy(term : Variable) -> sympy.Symbol:
    """Converts a variable to a sympy symbol"""
@overload
def termToSympy(term : Function) -> sympy.FunctionClass:
    """Converts a function to a sympy function class"""

@overload
def termToSympy(term : FuncTerm) -> sympy.Function:
    """Converts a functerm to a sympy function"""

def termToSympy(term):
    """Converts a term to a sympy term"""
    if isinstance(term, Constant):
        return sympy.Symbol(term.symbol + "_constant")
    if isinstance(term, Variable):
        return sympy.Symbol(term.symbol + "_variable")
    if isinstance(term, Function):
        return sympy.Function(term.symbol + "_" + str(term.arity))
    # Assume FuncTerm
    args = []
    for arg in term.arguments:
        args.append(termToSympy(arg))
    function_handle = termToSympy(term.function)
    return function_handle(*args)


@overload
def sympyToTerm(symterm : sympy.Symbol) -> Union[Variable, Constant]:
    """Converts a sympy symbol to either a variable or constant"""

@overload
def sympyToTerm(symterm : sympy.FunctionClass) -> Function:
    """Converts a sympy function class to a function"""

@overload
def sympyToTerm(symterm : sympy.Function) -> FuncTerm:
    """Converts a sympy function to a functerm"""

def sympyToTerm(symterm):
    """Converts a sympy term to a term"""
    if isinstance(symterm, sympy.Symbol):
        if symterm.name[-9:] == "_variable":
            return Variable(symterm.name[:-9])
        elif symterm.name[-9:] == "_constant":
            return Constant(symterm.name[:-9])
        else:
            raise ValueError("Sympy symbol must end in _variable or _constant")
    if isinstance(symterm, sympy.FunctionClass):
        index = symterm.name.find("_")
        if index == -1:
            raise ValueError("Function name must end with _arity where arity is a natural number")
        arity = int(symterm.name[(index + 1):])
        return Function(symterm.name[:index], arity)
    # Assume sympy's equivalent to FuncTerm
    if not isinstance(symterm.args, tuple):
        raise ValueError("Function must have arguments")
    args = []
    for arg in symterm.args:
        args.append(sympyToTerm(arg))
    function_handle = sympyToTerm(symterm.func)
    return function_handle(*args)