#!/usr/bin/env python3
from symcollab.algebra import Function, Variable, Constant, Equation
from symcollab.Unification.unif import unif

# Setting up terms
f = Function("f", 2)
g = Function("g", 1)
x = Variable("x")
y = Variable("y")
z = Variable("z")
a = Constant("a")
b = Constant("b")


# applying unification
#example 1: unifiable
print(unif({Equation(f(x, y), f(a, b))}))

#example 2: simple function clash
print(unif({Equation(f(x, y), g(z))}))

#example 3: function clash
print(unif({Equation(f(x, x), f(g(y), a))}))

#example 4: occurs check
print(unif({Equation(f(x, y), f(g(x), a))}))

#example 5: unifiable
print(unif({Equation(f(z, z), f(g(f(x, y)), g(f(a, b))))}))
