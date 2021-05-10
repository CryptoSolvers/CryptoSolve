from symcollab.algebra import Term, Function, Variable, Constant, FuncTerm, Equation
from symbolic_check import elim_f, elim_c, occurs_check
from typing import Tuple, Dict, List, Optional, Set
from symcollab.xor import xor
from symcollab.xor.structure import Zero
from symcollab.algebra.term import get_vars

def test_elimf():
	f  = Function("f", 1)
	xo = Function("f", 2)
	z  = Zero()
	c  = Constant("c")
	x  = Variable("x")
	b  = Variable("b")

	func = FuncTerm(f, [x])
	func2 = FuncTerm(f, [z])
	func3 = FuncTerm(xo, [c,b])

	eq1 = Equation(func, c)
	eq2 = Equation(xor(func, func3), z)
	eq3 = Equation(b, func)
	eq4 = Equation(func2, z)

	topf : Set[Equation] = {eq1, eq2, eq3, eq4}
	print("Testing elim_f with ", topf)
	new_set = elim_f(topf)
	print("Result ", new_set)

test_elimf()

print()

def test_elimc():
	c = Function("C", 3)
	p = Constant('p')
	q = Constant('q')
	i = Constant('i')
	j = Constant('j')
	a = Constant('1')
	x  = Variable("x")
	z  = Zero()

	func_pi = FuncTerm(c, [p, i, a])
	func_qj = FuncTerm(c, [q, j, a])

	eq1 = Equation(xor(func_pi, func_qj), z)
	eq2 = Equation(xor(func_qj, func_pi), z)
	eq3 = Equation(func_pi, x)

	topf : Set[Equation] = {eq1, eq2, eq3}
	print("Testing elim_c with ", topf)
	new_set = elim_c(topf)
	print("Result: ", new_set)
	print()

	b = Constant('2')

	func_pi = FuncTerm(c, [p, i, a])
	func_qj = FuncTerm(c, [q, j, b])

	eq1 = Equation(xor(func_pi, func_qj), z)
	eq2 = Equation(xor(func_qj, func_pi), z)

	topf : Set[Equation] = {eq1, eq2}
	print("Testing elim_c with ", topf)
	new_set = elim_c(topf)
	print("Result: ", new_set)

test_elimc()

print()

def test_occurs():
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

	eq1 = Equation(fyz, x)
	eq2 = Equation(y, gb)
	eq3 = Equation(b, fxz)
	eq4 = Equation(z, fba)

	occ = {eq1, eq2, eq3}
	print("Testing occurs check with ", occ)
	print("Was there an occurs check: ", occurs_check(occ))
	print()
	
	occ = {eq1, eq2, eq4}
	print("Testing occurs check with ", occ)
	print("Was there an occurs check: ", occurs_check(occ))
	
test_occurs()

print()