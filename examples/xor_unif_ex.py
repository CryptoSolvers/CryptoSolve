#!/usr/bin/env python3
from algebra import Function, Variable, Constant
from xor.xorhelper import *
from xor.structure import *

f = Function("f", 1)
x = Variable("x")
y = Variable("y")
z = Variable("z")
x1 = Variable("x1")
x2 = Variable("x2")
x3 = Variable("x3")
a = Constant("a")
b = Constant("b")
c = Constant("c")
d = Constant("d")
ze = Zero()

t1 = xor(x, f(y), f(x1))
t2 = xor(y, f(z), f(x2))
t3 = xor(z, f(x), f(x3))

eq1 = Equation(ze, t1)
eq2 = Equation(ze, t2)
eq3 = Equation(ze, t3)
equations = Equations([eq1, eq2, eq3])

#t1 = f(xor(x, y))
#t2 = x
#eq1 = Equation(t1, t2)
#equations = Equations([eq1])

result = xor_unification(equations)

print("Here are the unifiers:")
for res in result:
    print(res)

