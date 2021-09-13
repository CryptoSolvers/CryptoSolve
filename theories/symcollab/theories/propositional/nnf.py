"""
Algorithms to make a formula into
negation normal form and to check
whether it is in negation normal form
"""
from ..predicate import And, Connective, Exists, ForAll, Formula, \
    Iff, Imp, Not, Or, Predicate

__all__ = ['nnf', 'is_nnf']

def nnf(formula: Formula) -> Formula:
    """
    Takes a formula and returns
    the negation normal form of it.

    A formula is in negation normal form only if it is
    constructed using only binary connectives And/Or,
    ForAll, Exists as well as only having Not applied
    to predicates.
    """
    # Not Cases
    if isinstance(formula, Not):
        subformula = formula.subformula

        ## Not(Not(x0)) -> x0
        if isinstance(subformula, Not):
            return nnf(subformula.subformula)

        ## Not(ForAll(...)) or Not(Exists(...))
        if isinstance(subformula, (ForAll, Exists)):
            bound_var = subformula.bound_variable
            p = subformula.subformula
            ### Not(ForAll(x, p)) -> Exists(x, Not(p))
            if isinstance(subforumula, ForAll):
                return Exists(bound_var, nnf(Not(p)))
            ### Not(Exists(x, p)) -> ForAll(x, Not(p))
            return ForAll(bound_var, nnf(Not(p)))


        ## Not(And(...)), Not(Or(...))
        ## Not(Imp(...)), Not(Iff(...))
        if isinstance(subformula, Connective):
            x0 = subformula[0]
            x1 = subformula[1]
            ### Not(And(x00, x01)) -> Or(Not(x00), Not(x01))
            if isinstance(subformula, And):
                return Or(nnf(Not(x0)), nnf(Not(x1)))
            ### Not(Or(x00, x01)) -> And(Not(x00), Not(x01))
            if isinstance(subformula, Or):
                return And(nnf(Not(x0)), nnf(Not(x1)))
            ### Not(Imp(x00, x01)) -> And(x00, Not(x01))
            if isinstance(subformula, Imp):
                return And(nnf(x0), nnf(Not(x1)))
            ### Not(Iff(x00, x01)) -> Or(And(x00, Not(x01)), And(Not(x00), X01))
            if isinstance(subformula, Iff):
                return Or(And(nnf(x0), nnf(Not(x1))), And(nnf(Not(x0)), nnf(x1)))

    # And(...) / Or(...)
    if isinstance(formula, (And, Or)):
        return formula.__class__(nnf(formula[0]), nnf(formula[1]))

    # Imp(...)
    if isinstance(formula, Imp):
        # Imp(x0, x1) -> Or(Not(x0), x1)
        return Or(nnf(Not(formula[0])), nnf(formula[1]))

    # Iff(...)
    if isinstance(formula, Iff):
        x0 = formula[0]
        x1 = formula[1]
        # Iff(x0, x1) -> Or(And(x0, x1), And(Not(x0), Not(x1)))
        return Or(And(nnf(x0), nnf(x1)), And(nnf(Not(x0)), nnf(Not(x1))))

    # ForAll(...) / Exists(...)
    if isinstance(formula, (Exists, ForAll)):
        return formula.__class__(
            formula.bound_variable,
            nnf(formula.subformula)
        )

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

    # And/Or
    if isinstance(formula, (And, Or)):
        return is_nnf(formula[0]) and is_nnf(formula[1])

    # ForAll/Exists
    if isinstance(formula, (ForAll, Exists)):
        return is_nnf(formula.subformula)

    # Otherwise False (Iff, Imp, etc.)
    return False
