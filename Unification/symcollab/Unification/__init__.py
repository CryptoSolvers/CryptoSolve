from typing import Set
from symcollab.algebra import Equation, SubstituteTerm
from .unif import unif as syntactic_unif

__all__ = ['unify']

def unify(equations : Set[Equation], theory = None, rewriteSystem = None) -> Set[SubstituteTerm]:
    """
    Perform unification on a set of equations.
    Future capability includes considering the theory
    and rewrite system when calling a unification function.
    """
    if theory is not None or rewriteSystem is not None:
        raise NotImplementedError("Future capability: Please call individual unification function for now")
    return syntactic_unif(equations)
