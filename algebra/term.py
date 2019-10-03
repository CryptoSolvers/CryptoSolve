#!/usr/bin/env python3
import typing
from typing import Union, Any, Optional
import matplotlib.pyplot as plt
import networkx as nx
from copy import deepcopy

#
## Basic Types
#
class Function:
    def __init__(self, symbol : str, arity : int):
        assert arity >= 0
        self.symbol = symbol
        self.arity = arity
    def __call__(self, *args):
        return FuncTerm(self, args)
    def __repr__(self):
        return self.symbol
    def __hash__(self):
        return hash(self.symbol)
    def __eq__(self, x):
        return isinstance(x, Function) and self.symbol == x.symbol

class Variable: 
    def __init__(self, symbol : str):
        self.symbol = symbol
    def __repr__(self):
        return self.symbol
    def __eq__(self, x):
        return isinstance(x, Variable) and self.symbol == x.symbol
    def __hash__(self):
        return hash(self.symbol)

class FuncTerm:
    def __init__(self, function : Function, args): 
        self.function = function
        assert len(args) == self.function.arity
        self.arguments = args
    def __repr__(self):
        if self.function.arity == 0:
            return self.function.symbol
        return self.function.symbol + "(" + ", ".join(map(str, self.arguments)) + ")"
    # Hash needed for network library
    def __hash__(self):
        return hash((self.function, self.arguments))
    def __eq__(self, x):
        return isinstance(x, FuncTerm) and self.function == x.function and self.arguments == x.arguments
    def __contains__(self, term):
        inside = False
        for arg in self.arguments:
            if isinstance(arg, FuncTerm):
                inside = inside or (term in arg)
            else:
                inside = inside or (term == arg)
        return inside

class Constant(FuncTerm):
    def __init__(self, symbol : str):
        super(Constant, self).__init__(Function(symbol, 0), ())
    def __hash__(self):
        return hash(self.function.symbol)
    def __eq__(self, x):
        return isinstance(x, Constant) and self.function.symbol == x.function.symbol


# New Type to clean up future annotations
Term = Union[FuncTerm, Constant, Variable]

def get_vars(t: Term, unique = False):
	if isinstance(t, Variable): 
		return [t]
	
	l=[]
	if isinstance(t, FuncTerm):
		for i in t.arguments:
			l = l + get_vars(i)
	
	return set(l) if unique else l

def get_constants(t: Term, unique = False):
	if isinstance(t, Constant): 
		return [t]
	
	l=[]
	if isinstance(t, FuncTerm):
		for i in t.arguments:
			l = l + get_constants(i)
	
	return set(l) if unique else l


def get_vars_or_constants(t: Term, unique = False):
    if isinstance(t, Constant) or isinstance(t, Variable): 
        return [t]
    
    l=[]
    if isinstance(t, FuncTerm):
        for i in t.arguments:
            l = l + get_vars_or_constants(i)
    
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

