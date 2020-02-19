#!/usr/bin/env python3
import typing
from typing import Union, Any, Optional, List, Set, overload
from typing_extensions import Literal
from copy import deepcopy
from abc import ABC, abstractmethod # Abstract Base Class

#
## Basic Types
#
class AnySort:
    def __init__(self):
        self.name = "any"
        self.parents = {}
    def __repr__(self):
        return self.name
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, x):
        return self.name == x.name

ANY = AnySort()

class Sort(AnySort):
    def __init__(self, name, parent_sort = None):
        super().__init__()
        self.name = name
        self.parents = {ANY, parent_sort} | parent_sort.parents if parent_sort is not None else {ANY}
    def subset_of(self, sort) -> bool:
        """Returns true is this sort is a subset of the sort given"""
        return sort in self.parents
    # Syntactic sugar: You can compare sorts with <
    def __lt__(self, sort):
        return self.subset_of(sort)
    # Syntactic sugar: You can compare sorts with >
    def __gt__(self, sort):
        return sort.subset_of(self)


class Term(ABC):
    """A term is a FuncTerm, Variable, or Constant. This abstract class exists to provide shared functionality"""
    @abstractmethod # Don't allow this class to be instatiated on its own
    def __init__(self, symbol : str, sort : AnySort = ANY):
        self.symbol = symbol
        self.sort = sort # By default the sort will be ANY
    def __repr__(self):
        return self.symbol
    def __hash__(self):
        return hash(self.symbol)
    def __eq__(self, x):
        return type(self) == type(x) and self.symbol == x.symbol and self.sort == x.sort

class Function:
    def __init__(self, symbol : str, arity : int, domain_sort : Union[AnySort, List[AnySort]] = ANY, range_sort : AnySort = ANY):
        self.symbol = symbol
        self.domain_sort = domain_sort
        self.range_sort = range_sort
        assert arity >= 0
        self.arity = arity
        # If the domain sort is a list, make sure it has a one-to-one mapping with the arguments
        if isinstance(domain_sort, list):
            assert len(domain_sort) == arity
    def __call__(self, *args):
        # Check to see if arguments belong to the domain of the function
        for i, arg in enumerate(args):
            domain_sort = self.domain_sort if not isinstance(self.domain_sort, list) else self.domain_sort[i]
            if arg.sort != domain_sort and not arg.sort.subset_of(domain_sort):
                raise ValueError("Domain Mismatch. Expected {}, Got {}." % (str(domain_sort), str(arg.sort)))
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

class Variable(Term): 
    def __init__(self, symbol : str, sort : AnySort = ANY):
        super().__init__(symbol, sort)

class FuncTerm(Term):
    def __init__(self, function : Function, args): 
        super().__init__(function.symbol, function.range_sort)
        self.function = function
        assert len(args) == self.function.arity
        self.arguments = args
    def set_arguments(self, args):
        self.arguments = tuple(args)
    def set_function(self, function : Function):
        self.function = function
        self.sort = function.range_sort
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
        return type(self) == type(x) and self.function == x.function and self.arguments == x.arguments
    def __contains__(self, term):
        inside = False
        for arg in self.arguments:
            if isinstance(arg, FuncTerm) and arg.function.arity > 0:
                inside = inside or (term in arg)
            else:
                inside = inside or (term == arg)
        return inside

class Constant(FuncTerm):
    def __init__(self, symbol : str, sort : AnySort = ANY):
        super().__init__(Function(symbol, 0, range_sort = sort), ())

#
## get_vars Section
#

@overload
def get_vars(t: Term, unique: Literal[False]) -> List[Variable]:
	"""Get the variables inside a term"""

@overload
def get_vars(t: Term, unique : Literal[True]) -> Set[Variable]:
    """Get the variables inside a term"""
@overload
def get_vars(t: Term) -> List[Variable]:
    """Get the variables inside a term"""

def get_vars(t, unique = False):
    """Get the variables inside a term"""
    if isinstance(t, Variable): 
        return {t} if unique else [t]
	
    l : List[Variable] =[]
    if isinstance(t, FuncTerm):
        for i in t.arguments:
            l = l + get_vars(i, False)
    
    return set(l) if unique else l


#
## get_constants Section
#
@overload
def get_constants(t: Term, unique: Literal[False]) -> List[Constant]:
    """Get the constants inside a term"""

@overload
def get_constants(t: Term, unique: Literal[True]) -> Set[Constant]:
    """Get the constants inside a term"""

@overload
def get_constants(t: Term) -> List[Constant]:
    """Get the constants inside a term"""

def get_constants(t, unique = False):
    """Get the constants inside a term"""
    if isinstance(t, Constant): 
        return {t} if unique else [t]
	
    l : List[Constant] =[]
    if isinstance(t, FuncTerm):
        for i in t.arguments:
            l = l + get_constants(i, False)
    
    return set(l) if unique else l


#
## get_vars_or_constants Section
#
@overload
def get_vars_or_constants(t: Term, unique: Literal[False]) -> List[Union[Variable, Constant]]:
    """Get the variables and constants inside a term"""

@overload
def get_vars_or_constants(t: Term, unique: Literal[True]) -> Set[Union[Variable, Constant]]:
    """Get the variables and constants inside a term"""

@overload
def get_vars_or_constants(t: Term) -> List[Union[Variable, Constant]]:
    """Get the variables and constants inside a term"""

def get_vars_or_constants(t, unique = False):
    """Get the variables and constants inside a term"""
    if isinstance(t, Constant) or isinstance(t, Variable): 
        return {t} if unique else [t]
    
    l : List[Union[Variable, Constant]] = []
    if isinstance(t, FuncTerm):
        for i in t.arguments:
            l = l + get_vars_or_constants(i, False)
    
    return set(l) if unique else l


#
## Equation
#
class Equation:
    def __init__(self, l : Term, r : Term):
        self.left_side = l
        self.right_side = r
    
    def __repr__(self):
        return str(self.left_side) + " = " + str(self.right_side)

