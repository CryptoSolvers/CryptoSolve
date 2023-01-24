#!/usr/bin/env python3
from symcollab.algebra import Constant, Function, Variable, Equation
from symcollab.Unification.ac_unif import ac_unify

f = Function("f", 2)
g = Function("g", 1)
x = Variable("x")
y = Variable("y")
z = Variable("z")
a = Constant("a")
b = Constant("b")
lhs = f(x, y)
rhs = f(z, z)
e4 = Equation(lhs, rhs)
U4 = set()
U4.add(e4)

unifiers = ac_unify(U4)
print(next(iter(unifiers)))

