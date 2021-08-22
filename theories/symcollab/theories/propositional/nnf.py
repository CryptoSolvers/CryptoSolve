"""
Algorithms to make a formula into
negation normal form and to check
whether it is in negation normal form
"""
from ..predicate import And, Connective, Formula, \
    Iff, Imp, Not, Or, Predicate

__all__ = ['nnf', 'is_nnf']

def nnf(formula: Formula) -> Formula:
    """
    Takes a formula and returns
    the negation normal form of it.

    A formula is in negation normal form only if it is
    constructed using only binary connectives And/Or as well
    as only having Not applied to propositions.
    """
    if isinstance(formula, Not):
        subformula = formula.subformula
        # Not(Not(x0)) -> x0
        if isinstance(subformula, Not):
            return nnf(subformula.subformula)

        if isinstance(subformula, Connective):
            x0 = subformula[0]
            x1 = subformula[1]
            # Not(And(x00, x01)) -> Or(Not(x00), Not(x01))
            if isinstance(subformula, And):
                return Or(nnf(Not(x0)), nnf(Not(x1)))
            # Not(Or(x00, x01)) -> And(Not(x00), Not(x01))
            if isinstance(subformula, Or):
                return And(nnf(Not(x0)), nnf(Not(x1)))
            # Not(Imp(x00, x01)) -> And(x00, Not(x01))
            if isinstance(subformula, Imp):
                return And(nnf(x0), nnf(Not(x1)))
            # Not(Iff(x00, x01)) -> Or(And(x00, Not(x01)), And(Not(x00), X01))
            if isinstance(subformula, Iff):
                return Or(And(nnf(x0), nnf(Not(x1))), And(nnf(Not(x0)), nnf(x1)))

    if isinstance(formula, (And, Or)):
        return formula.__class__(nnf(formula[0]), nnf(formula[1]))

    if isinstance(formula, Imp):
        # Imp(x0, x1) -> Or(Not(x0), x1)
        return Or(nnf(Not(formula[0])), nnf(formula[1]))

    if isinstance(formula, Iff):
        x0 = formula[0]
        x1 = formula[1]
        # Iff(x0, x1) -> Or(And(x0, x1), And(Not(x0), Not(x1)))
        return Or(And(nnf(x0), nnf(x1)), And(nnf(Not(x0)), nnf(Not(x1))))

    return formula

def is_nnf(formula: Formula) -> bool:
    """
    Returns whether or not the formula
    is in Negation Normal Form.
    """
    if isinstance(formula, (bool, Predicate)):
        return True

    # Negation can only be applied to Predicates
    if isinstance(formula, Not):
        return isinstance(formula.subformula, (bool, Predicate))

    # Connectives Iff and Imp are not allowed
    if isinstance(formula, (Iff, Imp)):
        return False

    # Assume And/Or
    return is_nnf(formula[0]) and is_nnf(formula[1])
