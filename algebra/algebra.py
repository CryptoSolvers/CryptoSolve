#!/usr/bin/env python3
import typing
from typing import Union, Any, Optional
import matplotlib.pyplot as plt
import networkx as nx
from copy import deepcopy

#
## Basic Types
#

class Constant:
    def __init__(self, symbol : str):
        self.symbol = symbol
    def __repr__(self):
        return self.symbol
    def __eq__(self, x):
        return isinstance(x, Constant) and self.symbol == x.symbol
    def __hash__(self):
        return hash(self.symbol)

class Variable: 
    def __init__(self, symbol : str):
        self.symbol = symbol
    def __repr__(self):
        return self.symbol
    def __eq__(self, x):
        return isinstance(x, Variable) and self.symbol == x.symbol
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
        return isinstance(x, Function) and self.symbol == x.symbol

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

# New Type to clean up future annotations
Term = Union[FuncTerm, Constant, Variable]

#
## Directed Acyclic Graphs
#

class TermDAG:
    def __init__(self, term: Term):
        self.dag = nx.OrderedMultiGraph()
        self.term = term
        self.edge_labels = {}
        self.node_labels = {}
        self.dag.add_node(term)
        if isinstance(term, FuncTerm):
            self.node_labels[term] = term.function
            for index, t in enumerate(term.arguments):
                self._appendTermDAG(term, t, self.dag, label = str(index))
        else:
            self.node_labels[term] = term

    def _appendTermDAG(self, last_term : Term, term : Term, dag : nx.classes.digraph.DiGraph, label = ""):
        # Annotate edges with argument number
        if (last_term, term) in self.edge_labels and self.edge_labels[(last_term, term)] != label:
            self.edge_labels[(last_term, term)] = self.edge_labels[(last_term, term)] + ", " + label
        else:
            self.edge_labels[(last_term, term)] = label
        
        dag.add_edge(last_term, term)
        if isinstance(term, FuncTerm):
            # Go through each of the function arguments and add a directed edge to it
            for index, t in enumerate(term.arguments):
                self._appendTermDAG(term, t, dag, label = str(index))
            self.node_labels[term] = term.function
        else:
            self.node_labels[term] = term

    def show(self):
        fig = plt.figure()
        pos = nx.spring_layout(self.dag)
        nx.draw(self.dag, pos, font_weight = 'bold', node_size = 600, font_size = 30, node_color = ['#a8c74d'] + ['#1f78b4' for i in range(len(self.dag.nodes) - 1)])
        nx.draw_networkx_labels(self.dag, pos, labels = self.node_labels)
        nx.draw_networkx_edge_labels(self.dag, pos, edge_labels=self.edge_labels)
        fig.suptitle(self.term)
        plt.show()
    
    # Depth First Traversal
    def df_edge_traversal(self):
        return nx.dfs_edges(self.dag, source = list(self.dag.node)[0])
    def df_node_traversal(self):
        return nx.dfs_tree(self.dag, source = list(self.dag.node)[0])
    # Breadth First Traversal
    def bs_edge_traversal(self):
        return nx.bfs_edges(self.dag, source = list(self.dag.node)[0])
    def bs_node_traversal(self):
        return nx.bfs_tree(self.dag, source = list(self.dag.node)[0])
    
    def parents(self, term):
        if term in self.dag.node:
            return self.dag.predecessors(term)
        else:
            return []
#
## Equation
#

class Equation:
    def __init__(self, l : Term, r : Term):
        self.left_side = l
        self.right_side = r
    
    def __repr__(self):
        return str(self.left_side) + " = " + str(self.right_side)

# #
# ##
# ### Substitution Class
# ## Purpose: To hold substitutions and be able to apply them on a term
# #

# class Substitution:
#     def __init__(self):
#         self.subs = [] # Tuple of (Variable, TermDAG)
#     def add_substitution(self, variable, term):
#         assert isinstance(variable, Variable)
#         assert isinstance(term, Term) or isinstance(term, TermDAG)
        
#         td = None
#         if isinstance(term, Term):
#             td = TermDAG(term)
#         else:
#             td = term
        
#         self.subs.append((variable, td))

#     def apply_substitution(self, termdag):
#         new_dag = nx.OrderedDiGraph()
#         new_nodes = []
#         new_edges = []
#         ## Need to think of a way to handle substitutions so that
#         ## entire parts of a tree can be replaced
#         # nodes = termdag.df_node_traversal()
#         # variables, terms = zip(*self.subs)
#         # for (i, node) in enumerate(nodes):
#         #     if node in variables:
#         #         replacement = terms[variables.index(node)]
#         #         nodes[i] = replacement
#         new_dag.update(new_edges, new_nodes)
#         return new_dag


def termSubstituteHelper(term, variable, replacement_term):
    return_value = None
    if term == variable:
        return_value = replacement_term
    elif isinstance(term, FuncTerm):
        term.arguments = list(term.arguments)
        for i, t in enumerate(term.arguments):
            term.arguments[i] = termSubstituteHelper(t, variable, replacement_term)
        term.arguments = tuple(term.arguments)
        return_value = term
    else:
        return_value = term
    return return_value

def termSubstitute(term, variable, replacement_term):
    new_term = deepcopy(term)
    new_term = termSubstituteHelper(term, variable, replacement_term)
    return new_term

def termDAGSubstitute(dag, variable, replacement_term):
    root = list(dag.dag.node)[0]
    new_root = termSubstitute(root, variable, replacement_term)
    return TermDAG(new_root)