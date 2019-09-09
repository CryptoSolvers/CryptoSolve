#!/usr/bin/env python3
import typing
from typing import Union, Any, Optional
import matplotlib.pyplot as plt
import networkx as nx

#
## Basic Types
#

class Constant:
    def __init__(self, symbol : str):
        self.symbol = symbol
    def __repr__(self):
        return self.symbol
    def __eq__(self, x):
        return self.symbol == x.symbol
    def __hash__(self):
        return hash(self.symbol)

class Variable: 
    def __init__(self, symbol : str):
        self.symbol = symbol
    def __repr__(self):
        return self.symbol
    def __eq__(self, x):
        return self.symbol == x.symbol
    def __hash__(self):
        return hash(self.symbol)

class Function:
    # Should be Union[Function, Constant, Variable] instead of Any
    # but recursive types aren't supported
    # https://github.com/python/mypy/issues/731
    def __init__(self, symbol : str, *args : Any): 
        self.symbol = symbol
        self.arity = len(args)
        self.arguments = args
    # If the function doesn't have arguments we'll just display the name of the function
    # Otherwise we'll show function_name(arg1,arg2,...,argn)
    def __repr__(self):
        if self.arity == 0: return self.symbol
        return self.symbol + "(" + ", ".join(map(str, self.arguments)) + ")"
    # Hash needed for network library
    def __hash__(self):
        return hash((self.symbol, self.arguments))
    # Equality here is implemented for the network library
    # Since for the DAG we only care about the function name...
    # I left it to default behavior for the usual usage
    def __eq__(self, x):
        # If the arity is 0 and the symbols are the same, we say it's equal
        if self.arity == 0:
            if x == None:
                return False
            else:
                return self.symbol == x.symbol
        else:
            return self == x

# New Type to clean up future annotations
Term = Union[Function, Constant, Variable]

#
## Directed Acyclic Graphs
#

def createTermDAG(term : Term) -> nx.classes.digraph.DiGraph : 
    dag = nx.DiGraph()
    last_term = None
    dag = appendTermDAG(last_term, term, dag)
    return dag

def appendTermDAG(last_term : Optional[Term], term: Term, dag : nx.classes.digraph.DiGraph):
    # Here we need to be careful for if we're starting the graph or if the term is a function
    # If the term is a funciton, we need to only transfer the function name to the graph,
    # that way we can satisfy each symbol being unique
    # If this is the first term in the graph, we call add_node, otherwise add_edge
    if isinstance(term, Function):
        if last_term is None:
            dag.add_node(Function(term.symbol))
        else:
            dag.add_edge(last_term, Function(term.symbol))
        # Go through each of the function arguments and add a directed edge to it
        for t in term.arguments:
            appendTermDAG(Function(term.symbol), t, dag)
    else:
        if last_term is None:
            dag.add_node(term)
        else:
            dag.add_edge(last_term, term)
    return dag

def showDAG(dag : nx.classes.digraph.DiGraph):
    nx.draw(dag, with_labels = True)
    plt.show()

#
## Equation
#

class Equation:
    def __init__(self, l : Term, r : Term):
        self.left_side = l
        self.right_side = r
    
    def __repr__(self):
        return str(self.left_side) + " = " + str(self.right_side)

