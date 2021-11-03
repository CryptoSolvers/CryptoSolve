"""
Algorithms to make a formula into
conjunctive normal form and to check
whether it is in conjunctive normal form
"""
from typing import List, Optional, Tuple
from ..predicate import And, Formula, Not, \
    Or, Predicate, Proposition, Valuation
from .core import atoms, possible_valuations, prop_eval
from .literal import Clause, literals, negate
from .simplify import prop_simplify
from .nnf import nnf

__all__ = ['cnf', 'is_cnf', 'cnf_clauses', 'definitional_cnf']

def _create_cnf_subformula(valuation: Valuation) -> Formula:
    """
    Takes a valuation that leads to false and builds
    and Or statement from the negation of the valuation.
    """
    pred0, boolean0 = valuation.popitem()
    formula: Formula = Not(pred0) if boolean0 else pred0
    for pred, boolean in valuation.items():
        formula = Or(formula, Not(pred) if boolean else pred)
    return formula

def cnf(formula: Formula) -> Formula:
    """
    Takes a formula and returns its
    Conjunctive Normal Form.

    A formula is in conjunctive normal form if it is a
    conjunction of disjunctions.
    """

    # If there are no predicates, simplify the formula to True/False
    if len(atoms(formula)) == 0:
        return prop_simplify(formula)

    # Grab the valuations that make the formula false
    unsat_vals = [
        val for val in possible_valuations(atoms(formula)) \
        if not prop_eval(formula, val)
    ]

    # If there are no valuations that make the
    # formula false, then its True
    if len(unsat_vals) == 0:
        return True

    val0 = unsat_vals.pop()
    proposition = _create_cnf_subformula(val0)

    for val in unsat_vals:
        proposition = And(proposition, _create_cnf_subformula(val))

    return proposition

def is_cnf(formula: Formula, or_found: bool = False) -> bool:
    """
    Returns whether or not the formula is
    in Conjunctive Normal Form.
    """
    if isinstance(formula, (bool, Predicate)):
        return True

    # Negation can only be applied to Predicates
    if isinstance(formula, Not):
        return isinstance(formula.subformula, (bool, Predicate))

    if isinstance(formula, And):
        # An And cannot be under an Or
        if or_found:
            return False
        return is_cnf(formula[0], False) and is_cnf(formula[1], False)

    if isinstance(formula, Or):
        return is_cnf(formula[0], True) and is_cnf(formula[1], True)

    # Otherwise False (Iff, Imp, ForAll, Exists)
    return False

def cnf_clauses(formula: Formula, checked_cnf: bool = False) -> List[Clause]:
    """
    Takes a formula and returns a list of list of
    propositions (list of clauses) that represents its CNF.
    """
    # Formula must be in CNF
    if not checked_cnf and not is_cnf(formula):
        raise ValueError("Formula must be in Conjunctive Normal Form.")

    if isinstance(formula, (bool, Predicate, Not)):
        return [literals(formula)]
    if isinstance(formula, Or):
        return [literals(formula[0]) + literals(formula[1])]

    # Assume And since others will fail is_cnf check above
    x0 = formula[0]
    x1 = formula[1]
    return cnf_clauses(x0, True) + cnf_clauses(x1, True)

def _not_unique(prop: Proposition, formula: Formula) -> bool:
    """
    Returns whether or not the proposition is
    in the formula.
    """
    if isinstance(formula, (bool, Predicate)):
        return prop == formula
    return prop in formula

def _fresh_prop(formula: Formula) -> Proposition:
    """Creates a fresh proposition not in the formula x"""
    x_prime = Proposition("x'")
    while _not_unique(x_prime, formula):
        x_prime = Proposition(x_prime.name + "'")
    return x_prime

def _definitional_cnf_helper(formula: Formula, result: Optional[Formula] = None) -> Tuple[Formula, Formula]:
    """See Definitional CNF for details."""
    # Base Case
    if isinstance(formula, (bool, Predicate, Not)):
        if result is None:
            return formula, formula
        return formula, And(result, formula)

    if not isinstance(formula, (And, Or)):
        raise ValueError(f"Unexpected type '{formula.__class__.__name__}'")

    # We need to do all the work when we're going back
    # up the stack, so call the recursion first.
    x0, result0 = _definitional_cnf_helper(formula[0], None)
    x1, result1 = _definitional_cnf_helper(formula[1], None)
    result = And(result0, result1)

    # And Case
    if isinstance(formula, And) \
       and isinstance(x0, (bool, Predicate, Not)) \
       and isinstance(x1, (bool, Predicate, Not)):
        # We're going to define a fresh variable as the connective
        fprop = _fresh_prop(formula)
        # x <=> y ^ z is the same as
        # (-x V y) ^ (-x V z) ^ (x V -y V -z)
        # Note: negate used instead of Not to simplify Not(Not(x))
        return fprop, And(result, And(And(
            Or(Not(fprop), x0),
            Or(Not(fprop), x1)),
            Or(Or(fprop, negate(x0)), negate(x1))
        ))

    # Or Case
    if isinstance(formula, Or) \
       and isinstance(x0, (bool, Predicate, Not)) \
       and isinstance(x1, (bool, Predicate, Not)):
        # We're going to define a fresh variable as the connective
        fprop = _fresh_prop(formula)
        # x <=> y V z is the same as
        # (-x V y V z) ^ (x V -y) ^ (x V -z)
        # Note: negate used instead of Not to simplify Not(Not(x))
        return fprop, And(result, And(And(
            Or(Or(Not(fprop), x0), x1),
            Or(fprop, negate(x0))),
            Or(fprop, negate(x1))
        ))

    raise ValueError(f"Unexpected type {type(formula)}")

def definitional_cnf(formula: Formula) -> Formula:
    """
    Performs the Definitional CNF algorithm
    which produces an equisatisfiable formula
    that is in Conjunctive Nornmal Form.

    Warning: The formula is not necessarily logically
    equivalent to the given formula.
    """
    # If it is already in NNF, then it takes
    # the same amount of time to call nnf
    # as is_nnf
    formula = nnf(formula)

    _, result = _definitional_cnf_helper(formula)
    return result
