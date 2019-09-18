#!/usr/bin/env python3
from algebra import *

#
## Examples
#

# Simple Equation Printing
f = Function("f", 2)
x = Variable("X")
a = Constant("a")
e1 = Equation(x, a)
e2 = Equation(f("2", "2"), Constant("4"))
print(e1)
print(e2)

# Directed Acyclic Graphs
# From page 16
# F(g(x, a), g(x,a))
g = Function("g", 2)
dag = TermDAG(f(g(x, a), g(x, a)))
dag.show()

## Substitutions
sigma = SubstituteTerm()
# Add the mapping x -> a
sigma.add_substitution(x, a)
# Apply the substitution to the term f(x)b
sigma * f(x, b)