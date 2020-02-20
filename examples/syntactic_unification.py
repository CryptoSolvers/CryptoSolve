#!/usr/bin/env python3
from algebra import *
from Unification import *

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
unif(f(x, y), f(a, b))

#example 2: simple function clash
unif(f(x, y), g(z))

#example 3: function clash
unif(f(x, x), f(g(y), a))

#example 4: occurs check
unif(f(x, y), f(g(x), a))

#example 5: unifiable
unif(f(z, z), f(g(f(x, y)), g(f(a, b))))
