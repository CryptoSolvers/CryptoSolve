from symcollab.algebra import Term, Function, Variable, Constant, FuncTerm, Equation
from symbolic_check import elim_f, elim_c, occurs_check
from typing import Tuple, Dict, List, Optional, Set
from symcollab.xor import xor
from symcollab.xor.structure import Zero
from symcollab.algebra.term import get_vars

x = Variable("x")
f = Function("f", 1)
xo = Function("f", 2)
z = Zero()

#func = FuncTerm(f, [x])
#func2 = FuncTerm(f, [x])
#func3 = FuncTerm(xo, [c,b])


#test of elim_f
"""eq1 = Equation(f, c)
eq2 = Equation(xor(func, func3), c)
print(eq2)
args = eq2.left_side._arguments
print(eq2.left_side.function == xor)

eq2 = Equation(b, func)
eq3 = Equation(func2, z)
topf : Set[Equation] = set()
topf.add(eq1)
topf.add(eq2)
topf.add(eq3)
for eq in topf:
	print(eq)
print("elim f")
new_set = elim_f(topf)
for eq in new_set:
	print(eq)
"""


#test of elim_c
"""
c = Function("C", 3)
p = Constant('p')
q = Constant('q')
i = Constant('i')
j = Constant('j')
a = Constant('1')

func_pi = FuncTerm(c, [p, i, a])
func_qj = FuncTerm(c, [q, j, a])
eq1 = Equation(xor(func_pi, func_qj), z)
eq2 = Equation(xor(func_qj, func_pi), z)
eq3 = Equation(func_pi, x)
topf : Set[Equation] = set()
topf.add(eq1)
topf.add(eq2)
topf.add(eq3)
for eq in topf:
	print(eq)
print("elim c")
new_set = elim_c(topf)
print(len(new_set))
for eq in new_set:
	print(eq)
"""
f = Function("f", 1)
g = Function("g", 1)
y = Function("y", 1)
x = Variable("x")
z = Variable("z")
b = Variable("b")

f_x = FuncTerm(f, [x])
g_z = FuncTerm(g, [z])
y_b = FuncTerm(y, [b])


eq1 = Equation(f_x, g_z)
eq2 = Equation(g_z, y_b)
eq3 = Equation(b, f_x)

occ = {eq1, eq2, eq3}
print(occurs_check(occ, 10))