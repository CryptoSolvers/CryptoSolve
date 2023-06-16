#!/usr/bin/env python3
from symcollab.algebra import Constant, Function, Variable, Equation
from symcollab.Unification.syntactic_ac_unification import *


#Setup the variables and AC function
f = Function("f", 2)
x = Variable("x")
y = Variable("y")
z = Variable("z")
a = Constant("a")
b = Constant("b")
x1 = Variable("x1")
y1 = Variable("y1")
z1 = Variable("z1")

print(occurs_check_full({
    Equation(x, f(y, z)),
    Equation(y, f(x, x))
}))

