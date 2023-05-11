#!/usr/bin/env python3
from symcollab.algebra import Constant, Function, Variable, Equation
from symcollab.Unification.syntactic_ac_unification import *

def print_sol(sol):
    if len(sol) == 0:
        print("No Solution\n")
        return
    for i, s in enumerate(sol):
        print("Solution", i, s)
    print("")

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


#Example 1
e = Equation(f(x, y), f(x1, y1))
U = {e}
sol = synt_ac_unif(U) #For a single solution
# also sol = synt_ac)unif(U, True)
sol = synt_ac_unif(U, False) # For all solutions
print_sol(sol)

#Example 2
e = Equation(f(x,x), f(y,y))
U = {e}
sol = synt_ac_unif(U)
print_sol(sol)


#Example 3
e2 = Equation(f(x, x), f(f(y,y),f(z,z)))
U1 = {e2} 
sol = synt_ac_unif(U1)
print_sol(sol)

#Example 4
lhs = f(x,f(x, x))
rhs = f(y, f(y, z))
e1 = Equation(lhs, rhs)
U1 = {e1} 
sol = synt_ac_unif(U1) 
print_sol(sol)