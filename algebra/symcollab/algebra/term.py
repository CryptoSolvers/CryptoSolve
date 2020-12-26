"""
The term library is responsible for the creation of
fundamental algebraic structures such as variables,
constants, and functions and their combinations to make terms.

This library also contains helper functions that can be useful
in algorithms that operate on terms.
"""
from copy import deepcopy
from functools import partial
from typing import Union, List, Set, overload, Optional, Any
from typing_extensions import Literal

__all__ = [
    'Sort', 'Function', 'Variable',
    'FuncTerm', 'Constant', 'get_vars',
    'get_constants', 'get_vars_or_constants', 'depth',
    'count_occurence', 'Equation', 'Term']

#
## Basic Types
#

class Sort:
    """
    A set that holds symbolic terms.

    A sort is by default a subset of the universal sort
    though it can subsort of another sort if specified.

    Parameters
    ----------
    name : str
        The name of the sort.
    parent_sort : Sort
        The sort in which this sort is a subset of.

    Notes
    -----
    A real life example of this is the sort of fractions.
    The integer sort is a subsort of the fraction sort.

    Examples
    --------
    >>> from symcollab.algebra import Sort
    >>> fractions = Sort("Q")
    >>> integers = Sort("Z", parent_sort=fractions)
    >>> integers < fractions
    True
    """
    def __init__(self, name: str, parent_sort: Optional['Sort'] = None):
        super().__init__()
        self.name = name
        self.parents = {parent_sort} | parent_sort.parents \
            if parent_sort is not None else set()
    def subset_of(self, sort) -> bool:
        """Returns true is this sort is a subset of the sort given"""
        return sort in self.parents
    # Syntactic sugar: You can compare sorts with <, >
    def __lt__(self, sort):
        return self.subset_of(sort)
    def __repr__(self):
        return self.name
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, x):
        return self.name == x.name
    def __str__(self):
        return self.name
    def __deepcopy__(self, memo):
        new_sort = Sort(deepcopy(self.name))
        memo[id(self)] = new_sort
        dcopy = partial(deepcopy, memo=memo)
        new_sort.parents = set(map(dcopy, self.parents))
        return new_sort

class Function:
    """
    A symbolic representation of a function.

    This class provides a callable symbolic representation of a function
    that can be used to create instantiations of terms called FuncTerms.

    Parameters
    ----------
    symbol : str
        The symbol to print out in the textual representation.

    arity : int
        The number of arguments that this function takes.

    domain_sort : Union[AnySort, List[AnySort]], default=Any
        The sort in which to restrict the input to. Defaults to AnySort.
        If given a list of sorts, then each argument is matched to a sort.

    range_sort : AnySort
        The sort to restrict the output to.

    Examples
    --------
    >>> from symcollab.algebra import *
    >>> x = Variable("x")
    >>> f = Function("f", arity = 1)
    >>> f(x)
    f(x)
    """
    def __init__(self, symbol: str, arity: int,
                 domain_sort: Union[Optional[Sort], List[Optional[Sort]]] = None,
                 range_sort: Optional[Sort] = None):
        assert arity >= 0
        self.symbol = symbol
        self.domain_sort = domain_sort
        self.range_sort = range_sort
        self.arity = arity

        # If the domain sort is a list, make sure it has a one-to-one mapping with the arguments
        if isinstance(domain_sort, list):
            assert len(domain_sort) == arity

    def __call__(self, *args):
        """Ensure domain of arguments are valid and produce a FuncTerm."""
        for i, arg in enumerate(args):
            # Grab the specific argument from the domain_sort list if applicable
            domain_sort = self.domain_sort \
                if not isinstance(self.domain_sort, list) else self.domain_sort[i]

            if domain_sort is not None:
                error_message = "Domain Mismatch. Expected {}, Got {}.".format(
                    str(domain_sort), str(arg.sort))
                if arg.sort is None:
                    raise ValueError(error_message)
                if arg.sort != domain_sort and not arg.sort.subset_of(domain_sort):
                    raise ValueError(error_message)

        return FuncTerm(self, args)

    def __repr__(self):
        return self.symbol
    def __hash__(self):
        return hash((self.symbol, self.arity))
    def __eq__(self, x):
        return type(self) == type(x) \
            and self.symbol == x.symbol \
            and self.domain_sort == x.domain_sort \
            and self.range_sort == x.range_sort

class Variable:
    """
    A symbolic representation of a variable.

    Parameters
    ----------
    symbol : str
        The symbol to print out in the textual representation.
    sort : AnySort
        The sort in which the variable belongs to.

    Examples
    --------
    >>> from symcollab.algebra import Variable
    >>> Variable("x")
    x
    """
    def __init__(self, symbol: str, sort: Optional[Sort] = None):
        self.symbol = symbol
        self.sort = sort
    def __repr__(self):
        return self.symbol
    def __hash__(self):
        return hash(self.symbol)
    def __eq__(self, x):
        return type(self) == type(x) and self.symbol == x.symbol and self.sort == x.sort
    def __deepcopy__(self, memo):
        return Variable(self.symbol, self.sort)

class FuncTerm:
    """
    A symbolic representation of the instantiation of a function.

    Parameters
    ----------
    function : Function
        The function in which the FuncTerm was instantiated from.
    args : {Variable, Constant, FuncTerm}
        The arguments of the function.

    Examples
    --------
    >>> from symcollab.algebra import *
    >>> f = Function("f", 1)
    >>> a = Constant("a")
    >>> f(a)
    f(a)
    """
    def __init__(self, function: Function, args):
        assert len(args) == function.arity
        self.function = function
        self._arguments = args
    @property
    def sort(self):
        return self.function.range_sort
    @sort.setter
    def sort(self, s):
        self.function.range_sort = s
    @property
    def arguments(self):
        return self._arguments
    @arguments.setter
    def arguments(self, args):
        self._arguments = tuple(args)
    def __repr__(self):
        if self.function.arity == 0:
            return self.function.symbol
        return self.function.symbol + "(" + ", ".join(map(repr, self.arguments)) + ")"
    def __str__(self):
        if self.function.arity == 0:
            return self.function.symbol
        return self.function.symbol + "(" + ", ".join(map(str, self.arguments)) + ")"
    # Hash needed for network library
    def __hash__(self):
        return hash((self.function, tuple(self.arguments)))
    def __eq__(self, x):
        return type(self) == type(x) and \
            self.function == x.function and \
                self.arguments == x.arguments
    def __contains__(self, term):
        inside = False
        for arg in self.arguments:
            inside = inside or (term == arg)
            if isinstance(arg, FuncTerm) and arg.function.arity > 0:
                inside = inside or (term in arg)
        return inside
    def __deepcopy__(self, memo):
        arguments = map(deepcopy, self.arguments)
        return self.function(*arguments)


class Constant(FuncTerm):
    """
    A symbolic representation of a constant.

    Parameters
    ----------
    symbol : str
        The name of the constant.
    sort : AnySort
        The sort in which the constant belongs to.

    Notes
    -----
    For historical reasons, a constant is represented as a zero-arity FuncTerm.

    Examples
    --------
    >>> from symcollab.algebra import Constant
    >>> a = Constant("a")
    >>> a
    a
    """
    def __init__(self, symbol: str, sort: Optional[Sort] = None):
        super().__init__(Function(symbol, 0, range_sort=sort), ())
    @property
    def symbol(self):
        return self.function.symbol
    @symbol.setter
    def symbol(self, s):
        self.function.symbol = s
    def __deepcopy__(self, memo):
        return Constant(self.symbol, self.sort)


Term = Union[Variable, Constant, FuncTerm]

def _get_type(t: Term, unique: Literal[False], classinfo):
    """Recursively go through a term and pick out terms of type classinfo."""
    if isinstance(t, classinfo):
        return {t} if unique else [t]

    l : List[Any] = []
    if isinstance(t, FuncTerm):
        for i in t.arguments:
            l = l + _get_type(i, False, classinfo)

    return set(l) if unique else l


#
## get_vars Section
#

@overload
def get_vars(t: Term, unique: Literal[False]) -> List[Variable]:
    """Get the variables inside a term"""

@overload
def get_vars(t: Term, unique: Literal[True]) -> Set[Variable]:
    """Get the variables inside a term"""

def get_vars(t, unique=False):
    """
    Get the variables inside a term

    Parameters
    ----------
    t : Term
        The term to look for variables.
    unique : bool
        If true, then we only show each variable once.

    Examples
    --------
    >>> from symcollab.algebra import *
    >>> f = Function("f", 2)
    >>> x = Variable("x")
    >>> a = Constant("a")
    >>> get_vars(f(x, f(x, a)))
    [x, x]
    """
    return _get_type(t, unique, Variable)

#
## get_constants Section
#
@overload
def get_constants(t: Term, unique: Literal[False]) -> List[Constant]:
    """Get the constants inside a term"""
@overload
def get_constants(t: Term, unique: Literal[True]) -> Set[Constant]:
    """Get the constants inside a term"""

def get_constants(t, unique=False):
    """
    Get the constants inside a term

    Parameters
    ----------
    t : Term
        The term to look for constants.
    unique : bool
        If true, then we only show each constant once.

    Examples
    --------
    >>> from symcollab.algebra import *
    >>> f = Function("f", 2)
    >>> x = Variable("x")
    >>> a = Constant("a")
    >>> get_constants(f(x, f(x, a)))
    [a]
    """
    return _get_type(t, unique, Constant)


#
## get_vars_or_constants Section
#
@overload
def get_vars_or_constants(t: Term, unique: Literal[False]) -> List[Union[Variable, Constant]]:
    """Get the variables and constants inside a term"""
@overload
def get_vars_or_constants(t: Term, unique: Literal[True]) -> Set[Union[Variable, Constant]]:
    """Get the variables and constants inside a term"""
def get_vars_or_constants(t, unique=False):
    """
    Get the variables and constants inside a term

    Parameters
    ----------
    t : Term
        The term to look for variables and constants.
    unique : bool
        If true, then we only show each variable and constant once.

    Examples
    --------
    >>> from symcollab.algebra import *
    >>> f = Function("f", 2)
    >>> x = Variable("x")
    >>> a = Constant("a")
    >>> get_vars_or_constants(f(x, f(x, a)))
    [x, x, a]
    """
    return _get_type(t, unique, (Constant, Variable))


def depth(t: Term, depth_level: int = 0):
    """
    Returns the depth of a term.

    Parameters
    ----------
    t : Term
      The term to check the depth of.
    depth_level: int
      Used internally to keep track of the recursion

    Examples
    --------
    >>> from symcollab.algebra import *
    >>> f = Function("f", 2)
    >>> x = Variable("x")
    >>> a = Constant("a")
    >>> depth(f(f(x,a), f(x,a)))
    2
    """
    if isinstance(t, Variable) or isinstance(t, Constant) or isinstance(t, Function):
        return depth_level
    # Assume FuncTerm
    max_depth = 0
    for ti in t.arguments:
        max_depth = max(max_depth, depth(ti, depth_level + 1))
    return max_depth

def count_occurence(subterm: Term, term: Term):
    """
    Count the number of occurences
    of the subterm in the term.

    Examples
    ========
    >>> from symcollab.algebra import *
    >>> f = Function("f", 2)
    >>> h = Function("h", 1)
    >>> x = Variable("x")
    >>> count_occurence(h(x), f(h(x), f(x, h(x))))
    2
    """
    if subterm == term:
        return 1
    if isinstance(term, (Variable, Constant)):
        return 0
    count = 0
    for t in term.arguments:
        count += count_occurence(subterm, t)
    return count

#
## Equation
#
class Equation:
    """
    A structure to hold a unification problem.

    Parameters
    ----------
    l : Term
        The left hand side of the equation.
    r : Term
        The right hand side of the equation.

    Examples
    --------
    >>> from symcollab.algebra import *
    >>> x = Variable("x")
    >>> a = Constant("a")
    >>> Equation(x, a)
    x = a
    """
    def __init__(self, l: Term, r: Term):
        self.left_side = l
        self.right_side = r

    def __repr__(self):
        return str(self.left_side) + " = " + str(self.right_side)
