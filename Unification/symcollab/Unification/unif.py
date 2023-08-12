#!/usr/bin/env python3
"""
Slow Syntactic Unification
"""

from symcollab.algebra import Equation, SubstituteTerm
from typing import Set
from symcollab.Unification.common import (
    occurs_check, function_clash, eliminate,
    orient, decompose, delete_trivial
)
from symcollab.Unification.registry import Unification_Algorithms

# Franz Baader and Wayne Snyder. Unification Theory. Handbook of Automated Reasoning, 2001.
@Unification_Algorithms.register('')
def unif(equations: Set[Equation]) -> Set[SubstituteTerm]:
    """
    Perform syntactic unification on a set of equations
    and return a unifier as a set of
    """
    sigma = SubstituteTerm()
    while len(equations) > 0:
        if occurs_check(equations):
            return False # TODO: return set()
        if function_clash(equations):
            return False # TODO: return set() 
        equations, sigma = eliminate(equations, sigma)
        equations = orient(equations)
        equations = decompose(equations)
        equations = delete_trivial(equations)
    return sigma # TODO: return {sigma}
