"""Simplification rules for propositional logic"""
from ..predicate import Not, Formula, And, Or, Iff, Imp, Predicate

__all__ = ['prop_simplify']

def _prop_simplify_not(subformula: Formula):
    """
    Not Simplification rules under
    propositional logic.
    """
    # Not(Not(x)) -> x
    if isinstance(subformula, Not):
        return subformula.subformula
    # Not(True) -> False
    # Not(False) -> True
    if isinstance(subformula, bool):
        return not subformula
    return Not(subformula)

def _prop_simplify_and(subformula0: Formula, subformula1: Formula):
    """
    And simplification rules under
    propositional logic.
    """
    # And(x0, False) -> False
    # And(False, x1) -> False
    if not subformula0 or not subformula1:
        return False
    # And(True, x1) -> x1
    if subformula0:
        return subformula1
    # And(x0, True) -> x0
    if subformula1:
        return subformula0
    # And(x, Not(x)) -> False
    if isinstance(subformula1, Not) \
       and subformula0 == subformula1.subformula:
        return False
    # And(Not(x), x) -> False
    if isinstance(subformula0, Not) \
       and subformula1 == subformula0.subformula:
        return False
    # And(x, x) -> x
    if subformula0 == subformula1:
        return subformula0

    return And(subformula0, subformula1)

def _prop_simplify_or(subformula0: Formula, subformula1: Formula):
    """
    Or simplification rules under
    propositional logic.
    """
    # Or(True, x1) -> True
    # Or(x0, True) -> True
    if subformula0 == True or subformula1 == True:
        return True
    # Or(False, x1) -> x1
    if not subformula0:
        return subformula1
    # Or(x0, False) -> x0
    if not subformula1:
        return subformula0
    # Or(x, Not(x)) -> True
    if isinstance(subformula1, Not) \
       and subformula0 == subformula1.subformula:
        return True
    # Or(Not(x), x) -> True
    if isinstance(subformula0, Not) \
       and subformula1 == subformula0.subformula:
        return True
    # Or(x, x) -> x
    if subformula0 == subformula1:
        return subformula0
    return Or(subformula0, subformula1)

def _prop_simplify_imp(subformula0: Formula, subformula1: Formula):
    """
    Imp simplification rules under
    propositional logic.
    """
    # Imp(False, x1) -> True
    # Imp(x0, True) -> True
    if not subformula0 or subformula1 == True:
        return True
    # Imp(True, x1) -> x1
    if subformula0 == True:
        return subformula1
    # Imp(x0, False) -> Not(x0)
    if not subformula1:
        return Not(subformula0)
    # Imp(x, x) -> True
    if subformula0 == subformula1:
        return True
    return Imp(subformula0, subformula1)

def _prop_simplify_iff(subformula0: Formula, subformula1: Formula):
    """
    Iff simplification rules under
    propositional logic.
    """
    # Iff(True, x1) -> x1
    if subformula0 == True:
        return subformula1
    # Iff(x0, True) -> x0
    if subformula1 == True:
        return subformula0
    # Iff(False, x1) -> Not(x1)
    if not subformula0:
        return Not(subformula1)
    # Iff(x0, False) -> Not(x0)
    if not subformula1:
        return Not(subformula0)
    # Iff(x, x) -> True
    if subformula0 == subformula1:
        return True
    return Iff(subformula0, subformula1)

def prop_simplify(formula: Formula) -> Formula:
    """
    Simplifies a formula using
    propositional logic techniques.
    """
    # Base case
    if isinstance(formula, (bool, Predicate)):
        return formula

    # Not Cases
    if isinstance(formula, Not):
        subformula = prop_simplify(formula.subformula)
        return _prop_simplify_not(subformula)

    # Conjunctive Cases
    subformula0 = prop_simplify(formula[0])
    subformula1 = prop_simplify(formula[1])

    ## And Case
    if isinstance(formula, And):
        return _prop_simplify_and(subformula0, subformula1)

    ## Or Case
    if isinstance(formula, Or):
        return _prop_simplify_or(subformula0, subformula1)

    ## Implication Case
    if isinstance(formula, Imp):
        return _prop_simplify_imp(subformula0, subformula1)

    ## Iff Case
    if isinstance(formula, Iff):
        return _prop_simplify_iff(subformula0, subformula1)

    return formula
