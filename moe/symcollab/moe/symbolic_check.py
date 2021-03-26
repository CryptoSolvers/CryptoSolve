"""
Functions that check symbolically
the security of a mode of operation.

Based on Hai Lin's work.
"""

from typing import Tuple, Dict, List, Optional
from symcollab.algebra import Term, Function, Variable, Constant, FuncTerm, Equation
from symcollab.xor import xor

def elim_f()

def elim_c()

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

def pick_f()

def pick_c()

def pick_fail()

def symbolic_check()