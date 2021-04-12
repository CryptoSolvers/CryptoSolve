"""
Functions that check symbolically
the security of a mode of operation.

Based on Hai Lin's work.
"""

from typing import Tuple, Dict, List, Optional, Set
from symcollab.algebra import Term, Function, Variable, Constant, FuncTerm, Equation
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
		if isinstance(eq.right_side, FuncTerm):
			if eq.right_side.function == f and is_zero(eq.left_side):
				elim_f_set.remove(eq)

	return elim_f_set

"""
Given a list of sessions, which contain terms, find any f-rooted terms
that xor to zero and remove them, returning the new List
"""
def elim_c(sessions: List[List[Term]]) -> List[List[Term]]:
	elim_c_list = deepcopy(sessions)
	for i in range(0, len(sessions)-1):
		session1 = sessions[i]
		session2 = sessions[i+1]
		j = len(session1)-1
		while j >= 0:
			term1 = session1[j]
			k = len(session2)-1
			while k >= 0:
				term2 = session2[k]
				if isinstance(term1, FuncTerm) and isinstance(term2, FuncTerm):
					if term1.function == f and term2.function == f:
						if is_zero(xor(term1, term2)):
							elim_c_list[i].pop(j)
							elim_c_list[i+1].pop(k)
				k = k-1
			j = j-1

	return elim_c_list


"""
def occurs_check(e: Equation) -> bool:
	l = e.left_side
	r = e.right_side
	if (isinstance(r, Variable) and isinstance(l, FuncTerm)):
		temp = r
		r = l
		l = temp
	if isinstance(l, Variable) and isinstance(r, FuncTerm):
		if l in r:
			return True
	return False

def pick_f():

def pick_c():

def pick_fail():
"""