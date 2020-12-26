from .unif import unif
from symcollab.algebra import FuncTerm, Term, Variable
from typing import Dict, List

def p_syntactic(l: Term, r: Term, constraints : Dict[Variable, List[Term]]):
    """ p_syntactic is syntactic unification with the assurance that the unifier satisfies the constraints given"""
    sigma = unif(l, r)
    if sigma == False:
        return sigma
    sigma_domain, sigma_range = zip(*sigma.subs)
    for x, y in zip(sigma_domain, sigma_range):
        if isinstance(y, FuncTerm) and y not in constraints[x]:
            return False
    return sigma