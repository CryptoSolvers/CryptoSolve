"""
Functions that check symbolically
the security of a mode of operation.

Based on Hai Lin's work.
"""

from typing import Tuple, Dict, List, Optional, Set
from symcollab.algebra import Term, Function, Variable, Constant, FuncTerm, Equation
from symcollab.xor import xor
from symcollab.xor.structure import Zero, is_zero

zero = Zero()

#def moo_symbolic_check():

"""
Given a set of equations, remove any in the form of f(t) = 0
"""
def elim_f(top_f_terms: Set[Equation]) -> Set[Equation]:
	elim_f_set = set()
	for eq in top_f_terms:
		if isinstance(eq.left_side, FuncTerm) and is_zero(eq.right_side):
			elim_f_set.add(eq)
		if isinstance(eq.right_side, FuncTerm) and is_zero(eq.left_side):
			elim_f_set.add(eq)
	for eq in elim_f_set:
		top_f_terms.remove(eq)

	return top_f_terms

"""
def elim_c(ciphertexts: List[List[Term]]) -> List[List[Term]]:
	elim_c_list = ciphertexts
	for session in ciphertexts:
		for ciphertext in session:
			if xor(ciphertext)


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