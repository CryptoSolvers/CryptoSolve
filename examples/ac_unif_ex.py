#!/usr/bin/env python3
import sys
sys.path.append("..")


from algebra import *
from Unification import *
f = Function("f", 2)
g = Function("g", 1)
x = Variable("x")
y = Variable("y")
z = Variable("z")
a = Constant("a")
b = Constant("b")

t = f(x, x)
s = f(f(y, y), x)

ac_unify(t, s)
