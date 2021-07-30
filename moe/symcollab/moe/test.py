from symcollab.algebra import Term, Function, Variable, Constant, FuncTerm, Equation
from symbolic_check import *
from typing import Tuple, Dict, List, Optional, Set
from symcollab.xor import xor
from symcollab.xor.structure import Zero
from symcollab.xor.xorhelper import xor_to_list
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
	print()

def test_occurs():
	f = Function("f", 1)
	g = Function("g", 1)
	c = Function("C", 3)
	p = Constant('p')
	q = Constant('q')
	i = Constant('i')
	z = Variable("z")
	x = Variable("x")
	y = Variable("y")
	b = Variable("b")
	a = Variable("a")

	cpi = FuncTerm(c, [p, i, Constant("1")])
	fcpi = FuncTerm(f, [cpi])
	e1 = Equation(cpi, fcpi)
	e2 = Equation(x, FuncTerm(f, [g(x)]))
	e3 = Equation(x, FuncTerm(f, [b]))

	occ = {e1, e2, e3}
	print("Testing occurs check with ", occ)
	print("new set: ", occurs_check(occ))
	print()

def test_check_xor_structure():
	f = Function("f", 1)
	a = Constant("a")
	b = Constant("b")
	c = Constant("c")
	x = Variable("x")
	z = Zero()

	func = FuncTerm(f, [a])
	func1 = FuncTerm(f, [b])
	func2 = FuncTerm(f, [c])
	func3 = FuncTerm(f, [x])
	func4 = xor(func, func1)
	func5 = xor(func2, func3)

	eq1 = Equation(func, b)
	eq2 = Equation(func3, c)
	eq3 = Equation(func5, z)
	eq4 = Equation(xor(func2, func3), z)
	eq5 = Equation(xor(func4, func5), z)

	topf : Set[Equation] = {eq1, eq2, eq3, eq5}

	print("Testing pick_f with equation set: ", topf)
	print("Result pick_f: ", pick_f(topf))
	print()

def test_cbc_gen():
	res = cbc_gen(1,2)
	print("Testing CBC MOO generator: ", res)
	print()

def test_ex4_gen():
	res = ex4_gen(1,2)
	print("Testing EX4 MOO generator:", res)
	print()

def test_pick_fail():
	c = Function("C",3)
	f = Function("f",1)
	a = Constant("a")
	b = Constant('1')
	e = Constant("e")
	p = Constant('p')
	q = Constant('q')
	i = Constant('i')
	j = Constant('j')
	x  = Variable("x")
	z  = Zero()

	func = FuncTerm(f, [a])
	func2 = FuncTerm(f, [e])

	func_pi = FuncTerm(c, [p, i, b])
	func_qj = FuncTerm(c, [q, j, b])

	eq1 = Equation(func, z)
	eq2 = Equation(func_qj, x)
	eq3 = Equation(xor(func_pi, func), z)
	eq4 = Equation(xor(xor(func_pi, func), func2), z)

	topf : Set[Equation] = {eq1, eq4}
	print("Testing pick_fail with ", topf)
	new_set = pick_fail(topf, cbc_gen)
	print("Result: ", new_set)
	print()

	topf : Set[Equation] = {eq1, eq2, eq3}
	print("Testing pick_fail with ", topf)
	new_set = pick_fail(topf, ex4_gen)
	print("Result: ", new_set)
	print()

def test_pick_c():
	c = Function("C",3)
	f = Function("f",1)
	a = Constant("a")
	b = Constant('1')
	p = Constant('p')
	q = Constant('q')
	i = Constant('i')
	j = Constant('j')
	x  = Variable("x")
	z  = Zero()

	func = FuncTerm(f, [a])

	func_pi = FuncTerm(c, [p, i, b])
	func_qj = FuncTerm(c, [q, j, b])

	eq1 = Equation(func, z)
	eq2 = Equation(func_qj, x)
	eq3 = Equation(xor(func_pi, func), 0)

	topf : Set[Equation] = {eq1, eq2, eq3}
	print("Testing pick_c with ", topf)
	#new_set = pick_c(topf, 2, ) # Incomplete
	#print("Result: ", new_set)
	#print()

def test_algorithm():
	print("Checking symbolic security of MOO:", symbolic_cbc_gen("p", "i"))
	symbolic_check(symbolic_cbc_gen)

test_elimc()
test_elimf()
test_occurs()
test_check_xor_structure()
test_cbc_gen()
test_ex4_gen()
test_pick_fail()
#test_pick_c()
test_algorithm()
