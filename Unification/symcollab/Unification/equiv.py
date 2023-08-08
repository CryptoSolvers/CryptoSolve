from copy import deepcopy
from typing import Set
from symcollab.algebra import (
	Equation, Variable, FuncTerm,
	SubstituteTerm
)
from symcollab.Unification.unif import unif as syntactic_unification

def sub_to_equation(sigma: SubstituteTerm) -> Set[Equation]:
	"""Converts a substitution to a set of equations"""
	E = set()
	for (l, r) in sigma.subs:
		E.add(Equation(l, r))
	return E

def syntactic_equal(sigma1: SubstituteTerm, sigma2: SubstituteTerm) -> bool:
	"""
	Returns whether or not two substitutions are equivalent modulo
	variable renaming.
	"""
	S1 = sub_to_equation(sigma1)
	S2 = sub_to_equation(sigma2)
	S3 = S1.union(S2)

	unif = syntactic_unification(S3)
	if unif == False:
		return False

	unif_set = sub_to_equation(unif)

	# Discard non-variable mappings already existent
	# in the original substititions
	set_copy = deepcopy(unif_set)
	for x in unif_set:
		if isinstance(x.right_side, FuncTerm):
			if x in S3:
				set_copy.discard(x)

	# Any remaining non-variable mapping means that the
	# two equations are not equivalent modulo variable renaming
	for x in set_copy:
		if isinstance(x.right_side, Variable) and not isinstance(x.right_side, Variable):
			return False
	return True
