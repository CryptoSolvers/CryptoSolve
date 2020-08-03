"""
Collection of functions to check if a mode
of operation is invertible.
"""
from collections import Counter
from copy import deepcopy
from typing import Set
from algebra import Constant, depth, Function, FuncTerm, Term, TermDAG, Variable, get_constants, get_vars, get_vars_or_constants
from xor import xor
import numpy as np

__all__ = ['invert_simple', 'moo_invert', 'invert_gaussian']

def invert_gaussian(TermSet: Set[Term], P: Constant) -> bool:
	"""
	IN PROGRESS: 
	Based on the method developed by Veena. Goal is the plaintext
	constant P from a set of terms. Currently doesn't deal with 
	f.
	"""
	Vars = set()
	Cons = set()
	
	#Set of all the variables and constants for all the terms
	for t in TermSet:
		Vars.update(get_vars(t))
		Cons.update(get_constants(t))
	
	#Create an ordering for the variables
	term_items = list()
	for x in Cons.union(Vars):
		term_items.append(x)
	
	#create the linear system
	new_cons = len(TermSet)
	row_len = len(term_items) + new_cons
	M = []
	term_count = 0
	for t in TermSet:
		temp=[]
		for i in range(row_len):
			if i < len(term_items):
				if term_items[i] in get_vars_or_constants(t):
					temp.append(1)
				else:
					temp.append(0)
			else:
				if i - len(term_items) == term_count:
					temp.append(-1)
				else:
					temp.append(0)
		term_count = term_count + 1
		M.append(temp)
	B = np.zeros(new_cons)
	#Need to handle three cases here: (1) Square M, (2) Non-Square and row > col, (3) Non-Square col > row 
	if row_len == len(M): # m x n and m=n
		sol = np.linalg.solve(M, B)
	else: # m x n and m < n or m > n ### I think this works but may not get a unique solution!
		sol = np.linalg.lstsq(M,B,rcond=-1)[0]
	
	if sol.any():
		return(True)
	else:
		return(False)
	
	

def invert_simple(term):
    """
    Algorithm to get the plaintext P_{i} out of a MOO.

    Works by moving up in the DAG from the plaintext variable
    Applying the reverse transformation as it moves along
    f -> f^{-1}
    xor(P, x) -> xor(P, xor(x, x)) -> P

    Assumptions:
      - Previous plaintexts aren't in the term
      - The plaintext is only in one position
    """
    inverse_term = Variable("x")
    transforms = []

    # Create a TermDAG and check to see
    # that the plaintext is only in one position.
    d = TermDAG(term)
    assert Counter(d.leaves())[_P] == 1

    # Move up the DAG starting from the plaintext
    # leaf and add inverse operations to the
    # transforms list.
    current_term = deepcopy(_P)
    parent_term = list(d.parents(current_term))
    while parent_term != []:
        parent_term = parent_term[0]

        if parent_term.function == _f:
            transforms.append((_finv,))

        elif parent_term.function == xor:
            # Cancel out the xor by xoring with
            # the other argument again.
            if parent_term.arguments[0] == current_term:
                transforms.append((xor, parent_term.arguments[1]))
            else:
                transforms.append((xor, parent_term.arguments[0]))

        else:
            raise ValueError("A function other than f or xor detected")

        current_term = deepcopy(parent_term)
        parent_term = list(d.parents(parent_term))

    # Construct inverse term
    for transform in reversed(transforms):
        if transform[0] == _finv:
            inverse_term = _finv(inverse_term)
        else: # Assume xor
            inverse_term = xor(inverse_term, transform[1])

    return inverse_term


def moo_invert(K: Set[Term], nonces: Set[Constant], S: int, P: Term) -> bool:
	"""
	IN PROGRESS
	Given a set K of MOO interactions and max bound for the depth of a term,
	state whether or not a MOO term is invertible.
	Note, this is intentionally more general than is needed for the 
	strict invert problem for MOO programs and plaintext/var/con. 
	It can also consider terms and some constructed terms. 
	"""
	# Compute K*
	k_star = K | nonces
	# From K* construct C*
	c_star = deepcopy(k_star)
	current_length = 0
	while len(c_star) != current_length:
		current_length = len(c_star)
		temp = set()
		for t_1 in c_star:
			# Definition 11 (2a)
			if isinstance(t_1, FuncTerm) and str(t_1.function) == 'f':
				# Apply f inverse
				temp.update({t_1.arguments[0]})
			# Definition 11 (2b)
			for t_2 in c_star:
				new_term_b = xor(t_1, t_2)
				if depth(new_term_b) <= S:
					temp.add(new_term_b)
			# Definition 11 (2c)
			new_term_c = _f(t_1)
			if depth(new_term_c) <= S:
				temp.add(new_term_c)
		c_star.update(temp)
	# Check to see if the plaintext block is in any of the ground terms in c_star
	# xor library automatically maps terms to their ground terms
	#return _P in c_star
	for t in c_star:
		if P == t:
			return True
	return False

_#P = Variable("P_{i}")
_f = Function("f", 1)
_finv = Function("f^{-1}", 1)
