#!/usr/bin/env python3
from algebra import *

#
## Examples
#

# Simple Equation Printing
e1 = Equation(Variable("X"), Constant("a"))
e2 = Equation(Function("F", Constant("1"), Constant("2"), Constant("1")), Constant("4"))
print(e1)
print(e2)

# Directed Acyclic Graphs
# From page 16
# F(g(x, a), g(x,a))
dag = createTermDAG(Function("f",Function("g", Variable("x"), Constant("a")), Function("g", Variable("x"), Constant("a"))))
showDAG(dag)
