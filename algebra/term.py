#!/usr/bin/env python3
import typing
from typing import Union, Any, Optional, List, Set, overload
from typing_extensions import Literal
from copy import deepcopy

#
## Basic Types
#

class GenericTerm:
    def __init__(self, symbol : str):
        self.symbol = symbol
    def __repr__(self):
        return self.symbol
    def __hash__(self):
        return hash(self.symbol)
    def __eq__(self, x):
        return type(self) is type(x) and self.symbol == x.symbol
class Function(GenericTerm):
    def __init__(self, symbol : str, arity : int):
        super().__init__(symbol)
        assert arity >= 0
        self.arity = arity
    def __call__(self, *args):
        return FuncTerm(self, args)

class Variable(GenericTerm): 
    def __init__(self, symbol : str):
        super().__init__(symbol)
class FuncTerm(GenericTerm):
    def __init__(self, function : Function, args): 
        super().__init__(function.symbol)
        self.function = function
        assert len(args) == self.function.arity
        self.arguments = args
    def set_arguments(self, args):
        self.arguments = tuple(args)
    def set_function(self, function : Function):
        self.function = function
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
        return type(self) is type(x) and self.function == x.function and self.arguments == x.arguments
    def __contains__(self, term):
        inside = False
        for arg in self.arguments:
            if isinstance(arg, FuncTerm) and arg.function.arity > 0:
                inside = inside or (term in arg)
            else:
                inside = inside or (term == arg)
        return inside

class Constant(FuncTerm):
    def __init__(self, symbol : str):
        super().__init__(Function(symbol, 0), ())

# New Type to clean up future annotations
Term = Union[FuncTerm, Constant, Variable]

#
## get_vars Section
#
@overload
def get_vars(t: Term, unique: Literal[False]) -> List[Variable]:
	if isinstance(t, Variable): 
		return list([t])
	
	l : List[Variable] = []
	if isinstance(t, FuncTerm):
		for i in t.arguments:
			l = l + get_vars(i, False)
	
	return l

@overload
def get_vars(t: Term, unique : Literal[True]) -> Set[Variable]:
	return set(get_vars(t, False))

def get_vars(t: Term, unique : bool = False) -> Union[List[Variable], Set[Variable]]:
    return get_vars(t, unique)


#
## get_constants Section
#
@overload
def get_constants(t: Term, unique : Literal[False]) -> List[Constant]:
	if isinstance(t, Constant): 
		return list([t])
	
	l : List[Constant] = []
	if isinstance(t, FuncTerm):
		for i in t.arguments:
			l = l + get_constants(i, False)
	
	return l

@overload
def get_constants(t: Term, unique : Literal[True]) -> Set[Constant]:
	return set(get_constants(t, False))

def get_constants(t: Term, unique = False) -> Union[List[Constant], Set[Constant]]:
	return get_constants(t, unique)


#
## get_vars_or_constants Section
#
@overload
def get_vars_or_constants(t: Term, unique : Literal[False]) -> List[Union[Variable, Constant]]:
    if isinstance(t, Constant) or isinstance(t, Variable): 
        return list([t])
    
    l : List[Union[Variable, Constant]] = []
    if isinstance(t, FuncTerm):
        for i in t.arguments:
            l = l + get_vars_or_constants(i, False)
    
    return l

@overload
def get_vars_or_constants(t: Term, unique : Literal[True]) -> Set[Union[Variable, Constant]]:
    return set(get_vars_or_constants(t, False))

def get_vars_or_constants(t: Term, unique = False) -> Union[Set[Union[Variable, Constant]], List[Union[Variable, Constant]]]:
    return get_vars_or_constants(t, unique)

#
## Equation
#
class Equation:
    def __init__(self, l : Term, r : Term):
        self.left_side = l
        self.right_side = r
    
    def __repr__(self):
        return str(self.left_side) + " = " + str(self.right_side)

