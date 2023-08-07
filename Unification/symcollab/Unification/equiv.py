from copy import deepcopy
from symcollab.algebra import (
	get_vars, Equation, Variable, FuncTerm,
	Term, depth, get_vars_or_constants,
	SubstituteTerm
)
from symcollab.Unification.common import (
    delete_trivial, occurs_check, function_clash
)
from symcollab.Unification.unif import unif as syntactic_unification
from symcollab.Unification.registry import Unification_Algorithms
from typing import Set

def sub_to_equation(sigma: SubstituteTerm) -> Set[Equation]:
	lhs = sigma.domain()
	rhs = sigma.range()
	E = set()
	for l, r in zip(lhs, rhs):
		E.add(Equation(l, r))
	return E

def syntactic_equal(sigma1: SubstituteTerm, sigma2: SubstituteTerm):
	S1 = sub_to_equation(sigma1)
	S2 = sub_to_equation(sigma2)		
	S3 = S1.union(S2)
	print("S3: ")
	print(S3)
	unif = syntactic_unification(S3)
	print(unif)
	if unif == False:
		print("Not unifiable")
		return False
	unif_set = sub_to_equation(unif)
	set_copy =deepcopy(unif_set)
	for x in unif_set:
		if isinstance(x.right_side, FuncTerm):
			if x in S3:
				set_copy.discard(x)
	print(set_copy)
	for x in set_copy:
		if isinstance(x.right_side, Variable) and isinstance(x.right_side, Variable):
			return True
		else:
			return False
		

