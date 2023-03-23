#!/usr/bin/env python3
from symcollab.algebra import Constant, Function, Variable, Equation
from symcollab.Unification.ac_unif import ac_unify

a = Constant("a")
b = Constant("b")
c = Constant("c")

f = Function("f", 2)
g = Function("g", 1)

u = Variable("u")
x = Variable("x")
y = Variable("y")
z = Variable("z")

lhs = f(x, y)
rhs = f(z, z)
e = Equation(lhs, rhs)

print(e)
unifiers = ac_unify({e}, f)
print(next(iter(unifiers)))


#lhs = f(a, f(a, f(g(u), x)))
#rhs = f(b, f(g(c), f(y, z)))
#e = Equation(lhs, rhs)

#print(e)
#unifiers = ac_unify({e}, f)
#print(next(iter(unifiers)))

