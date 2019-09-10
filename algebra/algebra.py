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
    def __init__(self, symbol : str, arity : int):
        assert arity > 0
        self.symbol = symbol
        self.arity = arity
    def __call__(self, *args):
        return FuncTerm(self, args)
    def __repr__(self):
        return self.symbol
    def __hash__(self):
        return hash(self.symbol)
    def __eq__(self, x):
        return x is not None and self.symbol == x.symbol

class FuncTerm:
    def __init__(self, function : Function, args): 
        self.function = function
        assert len(args) == self.function.arity
        self.arguments = args
    def __repr__(self):
        return self.function.symbol + "(" + ", ".join(map(str, self.arguments)) + ")"
    # Hash needed for network library
    def __hash__(self):
        return hash((self.function, self.arguments))

# New Type to clean up future annotations
Term = Union[FuncTerm, Constant, Variable]

#
## Directed Acyclic Graphs
#

class TermDAG:
    def __init__(self, term: Term):
        self.dag = nx.DiGraph()
        self.term = term
        self.edge_labels = {}
        if isinstance(term, FuncTerm):
            self.dag.add_node(term.function)
            for t in term.arguments:
                self._appendTermDAG(term.function, t, self.dag)
        else:
            self.dag.add_node(term)
        

    def _appendTermDAG(self, last_term : Term, term : Term, dag : nx.classes.digraph.DiGraph, label = ""):
        if isinstance(term, FuncTerm):
            self.edge_labels[(last_term, term.function)] = label
            dag.add_edge(last_term, term.function)
            # Go through each of the function arguments and add a directed edge to it
            for index, t in enumerate(term.arguments):
                self._appendTermDAG(term.function, t, dag, label = str(index))
        else:
            self.edge_labels[(last_term, term)] = label
            dag.add_edge(last_term, term)

    def show(self):
        fig = plt.figure()
        pos = nx.spring_layout(self.dag)
        nx.draw(self.dag, pos, with_labels = True)
        nx.draw_networkx_edge_labels(self.dag, pos, edge_labels=self.edge_labels)
        fig.suptitle(self.term)
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

