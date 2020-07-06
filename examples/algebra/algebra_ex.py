#!/usr/bin/env python3
from algebra import Constant, Equation, Function, Sort, \
     SubstituteTerm, TermDAG, Variable

# Setting up terms
f = Function("f", 2)
g = Function("g", 2)
x = Variable("x")
y = Variable("y")
z = Variable("z")
a = Constant("a")
b = Constant("b")
c = Constant("c")

# Simple Equation Printing
e1 = Equation(x, a)
e2 = Equation(f(Constant("2"), Constant("2")), Constant("4"))
print(e1)
print(e2)

# Simple sort test
reals = Sort("reals")
non_zeros = Sort("non_zeros", reals)
divide = Function("divide", 2, [reals, non_zeros], reals)
one = Constant("1", non_zeros)
zero = Constant("0", reals)
try:
    divide(one, zero)
except Exception:
    print("Cannot divide by zero. Check.")

# Directed Acyclic Graphs
# From page 16
# F(g(x, a), g(x,a))
dag = TermDAG(f(g(x, a), g(x, a)))
dag.show()

## Substitutions
sigma = SubstituteTerm()
# Add the mapping x -> f(y)
sigma.add(x, g(y,c))
print(f(x, b))
print("Substitutions: ", sigma)
# Apply the substitution to the term f(x, b)
print(f(x, b) * sigma)
sigma2 = SubstituteTerm()
sigma2.add(y, a)
print("Another Substitution: ", sigma2)
print("Composing both substitutions and applying it to a term: f(x, b) * sigma * sigma2")
print(f(x, b) * sigma * sigma2)
