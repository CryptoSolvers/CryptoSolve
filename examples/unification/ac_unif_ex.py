#!/usr/bin/env python3
from algebra import Constant, Function, Variable, Equation
from Unification.ac_unif import ac_unify

f = Function("f", 2)
g = Function("g", 1)
x = Variable("x")
y = Variable("y")
z = Variable("z")
a = Constant("a")
b = Constant("b")

t = f(x, x)
s = f(f(y, y), x)


v = f(y,y)
w = f(z,z)
e1 = Equation(s,t)
e2 = Equation(v,w)
U = set()
U.add(e1)
U.add(e2)
U2=set()
U2.add(e1)

ac_unify(U)

ac_unify(U2)

