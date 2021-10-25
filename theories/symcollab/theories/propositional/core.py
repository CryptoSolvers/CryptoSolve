"""
Core functions in propositional logic.
"""
from copy import deepcopy
from typing import List, Optional, Union
from ..predicate import And, Connective, Exists, Formula, \
    ForAll, Imp, Iff, Not, Or, Predicate, Proposition, Set, Valuation

__all__ = [
    'prop_eval', 'atoms', 'possible_valuations',
    'satisfiable_valuations', 'tautology',
    'unsatisfiable', 'satisfiable',
    'is_propositional_formula'
]

# TODO: Maybe make a new type PropositionalFormula
PropositionalFormula = Union[bool, Proposition, Not, Connective]

def prop_eval(formula: Formula, valuation: Optional[Valuation] = None) -> bool:
    """
    Evaluate a propositional formula given a
    valuation dictionary v mapping Propositions to booleans.
    """
    if not is_propositional_formula(formula):
        raise ValueError("Formula provided to prop_eval is not a formula in propositional logic.")

    # Base Case
    if isinstance(formula, bool):
        return formula

    # Return the valuation of the predicate
    if isinstance(formula, Predicate):
        if valuation is None or formula not in valuation:
            raise ValueError(f"Predicate {formula.name} is not in valuation dictionary v.")
        return valuation[formula]

    # Not Case
    if isinstance(formula, Not):
        return not prop_eval(formula.subformula, valuation)

    # Assume Connective since others will cause
    # an error in is_propositional_formula check above
    subformula0 = prop_eval(formula[0], valuation)
    subformula1 = prop_eval(formula[1], valuation)
    if isinstance(formula, And):
        return subformula0 and subformula1
    if isinstance(formula, Or):
        return subformula0 or subformula1
    if isinstance(formula, Imp):
        return not subformula0 or subformula1
    if isinstance(formula, Iff):
        return subformula0 == subformula1

    raise ValueError(f"Unknown type {type(formula)}")

def atoms(formula: Formula) -> Set[Predicate]:
    """Returns a set of predicates in a formula."""
    if isinstance(formula, bool):
        return set()
    if isinstance(formula, Predicate):
        return {formula}
    if isinstance(formula, (Not, ForAll, Exists)):
        return atoms(formula.subformula)
    if isinstance(formula, Connective):
        return atoms(formula[0]) | atoms(formula[1])
    raise ValueError(f"Unexpected type {type(formula)}")

def possible_valuations(predicates: Set[Predicate],
  valuation: Optional[Valuation] = None) -> List[Valuation]:
    """
    Takes a set of predicates and returns a
    list of all possible valuations.
    """
    # We're going to recurse down on predicates

    if valuation is None:
        valuation = dict()

    # Base case
    if len(predicates) == 0:
        return [valuation]

    pred = predicates.pop()

    # Branch where pred is True
    predicates1 = deepcopy(predicates)
    valuation1 = deepcopy(valuation)
    valuation1[pred] = True

    # Branch where pred is False
    predicates2 = deepcopy(predicates)
    valuation2 = deepcopy(valuation)
    valuation2[pred] = False

    # Add branches to list
    return possible_valuations(predicates1, valuation1) \
           + possible_valuations(predicates2, valuation2)

def satisfiable_valuations(formula: Formula) -> List[Valuation]:
    """
    Takes a formula and returns a list
    of satisfiable valuations.
    """
    # Return only valuations that evaluate to true under the formula
    return [
        valuation for valuation in possible_valuations(atoms(formula)) \
        if prop_eval(formula, valuation)
    ]

def tautology(formula: Formula) -> bool:
    """
    Takes a formula and states
    whether its a tautology (always true)
    """
    # Return true if the formula is true for all possible valuations
    # of its predicates.
    return all(
        (prop_eval(formula, v) for v in possible_valuations(atoms(formula)))
    )

def unsatisfiable(formula: Formula) -> bool:
    """
    Naive implementation that takes
    a formula and returns true
    if the formula is unsatisfiable.
    """
    return tautology(Not(formula))

def satisfiable(formula: Formula) -> bool:
    """
    Naive implementation that takes
    a formula x and returns true if
    the formula is satisfiable.
    """
    return not unsatisfiable(formula)

def is_propositional_formula(formula: Formula) -> bool:
    """
    Returns whether or not a formula is
    a statement in propositional logic.
    """
    if isinstance(formula, (bool, Predicate)):
        return True

    if isinstance(formula, Not):
        return is_propositional_formula(formula.subformula)

    if isinstance(formula, Connective):
        return is_propositional_formula(formula[0]) \
               and is_propositional_formula(formula[1])

    # Otherwise return False (ForAll, Exists, etc.)
    return False
