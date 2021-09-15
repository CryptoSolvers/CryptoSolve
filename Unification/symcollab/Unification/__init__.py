from typing import Set
from symcollab.algebra import Constant, Equation, SubstituteTerm, Term, Variable
from symcollab.algebra.callable_registry import CallableRegistry


__all__ = ['Unification_Algorithms', 'unify']

# TODO: Enforce arity of two once the following signature is implemented
# Tuple[Set[Equation], Optional[Or[str, RewriteSystem]]] -> Set[SubstituteTerm]
Unification_Algorithms = CallableRegistry()

from .unif import unif as syntactic_unif

def _theories_in_term(t: Term) -> Set[str]:
    """
    Returns a set of all the theories functions
    have inside the term.
    """
    if isinstance(t, (Constant, Variable)):
        return set()
    # Assuming FuncTerm
    theories : Set[str] = {t.function.theory}
    for ti in t.arguments:
        theories |= _theories_in_term(ti)
    return theories

def unify(equations : Set[Equation]) -> Set[SubstituteTerm]:
    """
    Perform unification on a set of equations.
    It detects the theory the terms are under and
    calls the appropriate decision procedure.
    """
    theories : Set[str] = set()
    for equation in equations:
        theories |= _theories_in_term(equation.left_side)
        theories |= _theories_in_term(equation.right_side)
    if len(theories) > 1:
        raise NotImplementedError("Combination Theories are currently not supported.")
    theory = next(iter(theories))
    decision_procedure = Unification_Algorithms.find(theory)
    if decision_procedure is None:
        # See if we can find a unifier with syntactic unification
        unifiers = syntactic_unif(equations)
        if unifiers is False:
            raise NotImplementedError(
                f"A decision procedure for the theory {theory} \
                  has not been implemented. Also no \
                  syntactic unifiers found.")
        return unifiers
    return decision_procedure(equations)
