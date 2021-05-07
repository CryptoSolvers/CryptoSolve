from symcollab.algebra import Term, Function, Variable, Constant, FuncTerm, Equation
from symcollab.rewrite import RewriteRule
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
f = Function("f", 2)
g = Function("g", 1)
z = Variable("z")
x = Variable("x")
y = Variable("y")
b = Variable("b")
a = Variable("a")

fyz = FuncTerm(f, [y, z])
gb = FuncTerm(g, [b])
fxz = FuncTerm(f, [x, z])
fba = FuncTerm(f, [b, a])

"""
r = RewriteRule(x, b)
print(f_x)

print("Applying rewrite rule")

new = r.apply(y(g(f(f(x)))))
print(new.items())
for item in new.items():
	print(item)

print(isinstance(new['1'], FuncTerm))
"""
eq1 = Equation(fyz, x)
eq2 = Equation(y, gb)
eq3 = Equation(b, fxz)
eq4 = Equation(z, fba)
print(eq1)
print(eq2)
print(eq3)

occ = {eq1, eq2, eq3}
print(occurs_check(occ))

print(eq1)
print(eq2)
print(eq4)
occ = {eq1, eq2, eq4}
print(occurs_check(occ))
