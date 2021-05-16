"""
Functions that check symbolically
the security of a mode of operation.

Based on Hai Lin's work.
"""

from typing import Tuple, Dict, List, Optional, Set
from symcollab.algebra import Term, Function, Variable, Constant, FuncTerm, Equation, get_vars
from symcollab.xor import xor
from symcollab.xor.structure import Zero, is_zero
from copy import deepcopy

f = Function("f", 1)
zero = Zero()
c = Function("C", 3)
p = Constant('p')
q = Constant('q')
i = Constant('i')
j = Constant('j')

#def moo_symbolic_check(sigma: Set[Equation], cipherblock: Equation):

"""
Given a set of equations, remove any in the form of f(t) = 0, returning
the new list
"""
def elim_f(sigma: Set[Equation]) -> Set[Equation]:
	elim_f_set = deepcopy(sigma)
	for eq in sigma:
		if isinstance(eq.left_side, FuncTerm):
			if eq.left_side.function == f and is_zero(eq.right_side):
				elim_f_set.remove(eq)
		elif isinstance(eq.right_side, FuncTerm):
			if eq.right_side.function == f and is_zero(eq.left_side):
				elim_f_set.remove(eq)

	return elim_f_set

"""
Given a set of equations, remove those in the form of 
C_{p,i-a} xor C_{q, j-a} = 0, where i!=j
"""
def elim_c(sigma: Set[Equation]) -> Set[Equation]:
	elim_c_set = deepcopy(sigma)
	for eq in sigma:
		args = None
		if isinstance(eq.left_side, FuncTerm):
			if eq.left_side.function == xor and is_zero(eq.right_side):
				args = eq.left_side.arguments
		elif isinstance(eq.right_side, FuncTerm):
			if eq.right_side.function == xor and is_zero(eq.left_side):
				args = eq.right_side.arguments
		if args!= None and len(args) == 2:
			t1 = args[0]
			t2 = args[1]
			t1_is_c = False
			t2_is_c = False
			a1 = None
			a2 = None
			if t1.function == c and t2.function == c:
				cargs1 = t1.arguments
				cargs2 = t2.arguments
				if len(cargs1) == 3 and len(cargs2) == 3:
					a1 = cargs1[2]
					a2 = cargs2[2]
					if cargs1[0] == p and cargs1[1] == i:
						t1_is_c = True
						if cargs2[0] == q and cargs2[1] == j:
							t2_is_c = True
					elif cargs1[0] == q and cargs1[1] == j:
						t1_is_c = True
						if cargs2[0] == p and cargs2[1] == i:
							t2_is_c = True
			if t1_is_c and t2_is_c and a1 == a2:
				elim_c_set.remove(eq)
	return elim_c_set

def occurs_check(sigma: Set[Equation]) -> Set[Equation]:
	occurs_set = deepcopy(sigma)
	for e in sigma:
		t1 = e.left_side
		t2 = e.right_side
		if isinstance(t2, FuncTerm) and t1 in t2 or isinstance(t1, FuncTerm) and t2 in t1:
			occurs_set.remove(e)

	return occurs_set

"""
def pick_f(sigma: Set[Equation]) -> Set[Equation]:

def pick_c(sigma: Set[Equation], cipherblock: Equation) -> Set[Equation]:

def pick_fail(sigma: Set[Equation], cipherblock: Equation) -> Set[Equation]:
	for eq in sigma:
		args = None
		if isinstance(eq.left_side, FuncTerm):
			if eq.left_side.function == xor and is_zero(eq.right_side):
				args = eq.left_side.arguments
		elif isinstance(eq.right_side, FuncTerm):
			if eq.right_side.function == xor and is_zero(eq.left_side):
				args = eq.right_side.arguments
		if args != None && len(args) == 2:
			cpi = args[0]
			t = args[1]
"""

"""
# old code that might be useful for something else but isnt applicable in this situation

def found_cycle(t1, t2) -> bool:
	if t1 in t2 or t2 in t1:
		occurs_set.remove(e)
	elif isinstance(t1, FuncTerm):
		args = t1.arguments
		for arg in args:
			detect = found_cycle(arg, t2)
			if detect:
				return detect
	elif isinstance(t2, FuncTerm):
		args = t2.arguments
		for arg in args:
			detect = found_cycle(arg, t1)
			if detect:
				return detect

Given a set of equations, returns true if an occurs check exists 
def occurs_check(sigma: Set[Equation]) -> bool:
	for e in sigma:
		var = None
		term = None
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			var = e.left_side
			term = e.right_side
		elif isinstance(e.right_side, Variable) and isinstance(e.left_side, FuncTerm):
			var = e.right_side
			term = e.left_side
		if var != None and term != None:
			if var in term:
				return True
			check_vars = set(get_vars(term))
			check_eq = deepcopy(sigma)
			check_eq.remove(e)
			if found_cycle(var, check_vars, check_eq):
				return True
	return False

Returns true when a cycle is found, which occurs when a variable is written in terms of itself
def found_cycle(target: Variable, check: Set[Variable], equations: Set[Equation]) -> bool:
	for var in check:
		if var == target:
			return True

		for e in equations:
			term = None
			if isinstance(e.left_side, Variable) and var == e.left_side:
				term = e.right_side
			elif isinstance(e.right_side, Variable) and var == e.right_side:
				term = e.left_side
			if term != None:
				eq = deepcopy(equations)
				eq.remove(e)
				return found_cycle(target, get_vars(term), eq)
	return False
"""