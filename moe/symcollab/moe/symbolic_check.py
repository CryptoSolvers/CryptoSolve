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

#def moo_symbolic_check():

"""
Given a set of equations, remove any in the form of f(t) = 0, returning
the new list
"""
def elim_f(top_f_terms: Set[Equation]) -> Set[Equation]:
	elim_f_set = deepcopy(top_f_terms)
	for eq in top_f_terms:
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
def elim_c(top_f_terms: Set[Equation]) -> Set[Equation]:
	elim_c_set = deepcopy(top_f_terms)
	c = Function("C", 3)
	p = Constant('p')
	q = Constant('q')
	i = Constant('i')
	j = Constant('j')
	for eq in top_f_terms:
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
			if a1 == a2:
				elim_c_set.remove(eq)
	return elim_c_set

"""
Given a set of equations, returns true if an occurs check exists 
"""
def occurs_check(top_f_terms: Set[Equation]) -> bool:
	for e in top_f_terms:
		var = None
		term = None
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			var = e.left_side
			term = e.right_side
		elif  isinstance(e.right_side, Variable) and isinstance(e.left_side, FuncTerm):
			var = e.right_side
			term = e.left_side
		if var != None and term != None:
			if var in term:
				return True
			check_vars = set(get_vars(term))
			check_eq = deepcopy(top_f_terms)
			check_eq.remove(e)
			if found_cycle(var, check_vars, check_eq):
				return True
	return False

"""
Returns true when a cycle is found, which occurs when a variable is written in terms of itself
"""
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
def pick_f():

def pick_c():

def pick_fail():
"""