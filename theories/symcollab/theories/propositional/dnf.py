"""
Algorithms to make a formula into
disjunction normal form and to check
whether it is in disjunction normal form
"""
from typing import List
from ..predicate import And, atoms, Formula, \
    Iff, Imp, Not, Or, Predicate, \
    satisfiable_valuations, Valuation
from .literal import Clause, literals
from .simplify import prop_simplify


__all__ = ['dnf', 'is_dnf', 'dnf_clauses']

def _create_dnf_subformula(valuation: Valuation) -> Formula:
    """
    Takes a valuation that leads the formula to be true and
    builds an And statement from predicates and Not.
    """
    pred0, boolean0 = valuation.popitem()
    formula: Formula = pred0 if boolean0 else Not(pred0)
    for pred, boolean in valuation.items():
        formula = And(formula, pred if boolean else Not(pred))
    return formula

def dnf(formula: Formula) -> Formula:
    """
    Takes a formula and returns its
    Disjunctive Normal Form.

    A formula is in Disjunctive Normal form if it is
    a disjunction of conjunctions.
    """
    # If there are no predicates, simplify the formula to True/False
    if len(atoms(formula)) == 0:
        return prop_simplify(formula)

    sat_valuations = satisfiable_valuations(formula)

    # If there is no satisfiable valuations, then
    # its normal form is False
    if len(sat_valuations) == 0:
        return False

    val0 = sat_valuations.pop()
    subformula = _create_dnf_subformula(val0)

    for val in sat_valuations:
        subformula = Or(subformula, _create_dnf_subformula(val))

    return subformula

def is_dnf(formula: Formula, and_found: bool = False) -> bool:
    """
    Returns whether or not the formula
    is in Disjunctive Normal Form.
    """
    if isinstance(formula, (bool, Predicate)):
        return True

    # Negation can only be applied to Predicates
    if isinstance(formula, Not):
        return isinstance(formula.subformula, (bool, Predicate))

    # Connectives Iff and Imp are not allowed
    if isinstance(formula, (Iff, Imp)):
        return False

    if isinstance(formula, And):
        return is_dnf(formula[0], True) and is_dnf(formula[1], True)

    if isinstance(formula, Or):
        # And Or cannot be under and And
        if and_found:
            return False
        return is_dnf(formula[0], False) and is_dnf(formula[1], False)

    raise ValueError(f"Unknown type: {formula.__class__.__name__}")

def dnf_clauses(formula: Formula, checked_dnf: bool = False) -> List[Clause]:
    """
    Takes a formula and returns a list of list of
    predicates (list of clauses) that represents its DNF.
    """
    # Formula must be in DNF
    if not checked_dnf and not is_dnf(formula):
        raise ValueError("Formula must be in Disjunctive Normal Form.")

    if isinstance(formula, (bool, Predicate, Not)):
        return [literals(formula)]
    if isinstance(formula, And):
        return [literals(formula[0]) + literals(formula[1])]

    # Assume Or
    subformula0 = formula[0]
    subformula1 = formula[1]
    return dnf_clauses(subformula0, True) + dnf_clauses(subformula1, True)
