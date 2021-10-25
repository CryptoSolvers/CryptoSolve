"""
A literal is a boolean, a predicate, or
a Not with a boolean or predicate as
its subformula.
"""
from typing import List, Union
from ..predicate import Not, Predicate, Formula
from .nnf import is_nnf

__all__ = [
    'Literal', 'Clause', 'is_literal',
    'negate', 'is_negative', 'is_positive', 'literals'
]


Literal = Union[Not, Predicate, bool]
Clause = List[Literal]

def is_literal(formula: Formula) -> bool:
    """
    Returns whether or not a formula x is
    a literal.
    """
    if isinstance(formula, Not):
        subformula = formula.subformula
        return isinstance(subformula, (bool, Predicate))
    return isinstance(formula, (bool, Predicate))

def negate(literal: Literal) -> Literal:
    """Takes a literal and negates it."""
    if not is_literal(literal):
        raise ValueError("Function 'negate' only accepts literals.")
    if isinstance(literal, Not):
        return literal.subformula
    return Not(literal)

def is_negative(literal: Literal) -> bool:
    """
    Returns whether or not a literal is positive,
    which means it has a Not.
    """
    if not is_literal(literal):
        raise ValueError("Function 'is_positive' only accepts literals.")
    return isinstance(literal, Not)

def is_positive(literal: Literal) -> bool:
    """
    Returns whether or not a literal is positive,
    which means it does not have a Not.
    """
    return not is_negative(literal)

def literals(formula: Formula, checked_nnf: bool = False) -> List[Literal]:
    """
    Returns a list of Propositions or their
    negations for formulas in NNF.
    """
    if not checked_nnf and not is_nnf(formula):
        raise ValueError("Function 'literals' expects formula in NNF.")
    if isinstance(formula, (bool, Predicate, Not)):
        return [formula]
    # Assume connective since others will raise an error
    # in is_nnf
    return literals(formula[0], True) + literals(formula[1], True)
