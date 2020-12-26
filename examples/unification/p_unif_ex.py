#!/usr/bin/env python3
from symcollab.algebra import Constant, Function, Variable, Equation
from symcollab.xor.xorhelper import *
from symcollab.xor.structure import *
from symcollab.Unification.p_unif import p_unif
from symcollab.xor import *

f = Function("f", 1)
h = Function("h", 1)
x = Variable("x")
y = Variable("y")
z = Variable("z")
x1 = Variable("x1")
x2 = Variable("x2")
x3 = Variable("x3")
x4 = Variable("x4")
a = Constant("a")
b = Constant("b")
c = Constant("c")
d = Constant("d")
zero = Zero()




#The CBC mode is modeled as: [c, x1, t1, x2, t2, ......]
#where t1 = f(xor(c, x1) and t2 = f(xor(x2, t1))
t1 = f(xor(c, x1))
t2 = f(xor(x2, t1))
#The constraints are modeled using a dictionary in Python.
#So x1 can take any term from constraints[x1] and terms built up using "h" and "xor"
#x2 is similar
constraints1 = {x1: [c, zero], x2: [c, zero, x1, t1]}
#trying to unify t1 and t2
eq1 = Equation(t1, t2)
eqs1 = Equations([eq1])

result = p_unif(eqs1, constraints1)

print("Here are the P-unifiers:")
for r in result:
    print(r)


#Here is another mode, modeled as [a, x1, f(a), x2, f(x2), x3, b, x4, f(xor(h(f(x1)), f(x4), f(b)))]
''''
t3 = f(x2)
t4 = f(xor(h(f(x1)), f(x4), f(b)))

eq2 = Equation(t3, t4)
eqs2 = Equations([eq2])

constraints2 = {x1: [a, zero], x2: [a, zero, x1, f(a)], x3: [a, zero, x1, f(a), x2, t3], x4: [a, zero, x1, f(a), f(x2), t3, x3, b]}

result = p_unif(eqs2, constraints2)

print("Here are the P-unifiers:")
for r in result:
    print(r)
'''
