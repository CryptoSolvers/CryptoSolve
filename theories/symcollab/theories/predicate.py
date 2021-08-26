"""Encoding of Predicate Logic"""
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, NamedTuple, List, Optional, Set, Union
from symcollab.algebra import Term

__all__ = [
    'Relation', 'Predicate', 'Proposition',
    'Connective', 'And', 'Or', 'Imp', 'Iff',
    'Not', 'Formula', 'Valuation', 'prop_eval',
    'atoms', 'possible_valuations', 'satisfiable_valuations',
    'tautology', 'unsatisfiable', 'satisfiable',
    'is_propositional_formula'
]

class Relation:
    """
    A relation takes terms in
    order to create a predicate.
    """
    def __init__(self, name: str, arity: int):
        assert arity >= 0
        self.name = name
        self.arity = arity

    def __call__(self, *args):
        assert len(args) == self.arity
        assert all(lambda x: isinstance(x, Term), args)
        return Predicate(self, args)

    def __repr__(self):
        return f"Relation(name={self.name}, arity={self.arity})"

    def __eq__(self, other):
        return type(self) == type(other) \
            and self.name == other.name \
            and self.arity == other.arity

class Predicate:
    """
    A statement that can either be
    true or false in first order logic.
    """
    def __init__(self, relation: Relation, args: List[Term]):
        self.relation = relation
        self.args = args
    @property
    def name(self):
        """Returns the name of the proposition."""
        return self.relation.name
    def __hash__(self):
        return hash(("Predicate", self.relation, self.args))
    def __repr__(self):
        return f"{self.relation.name}({', '.join(map(repr, self.args))})"
    def __eq__(self, other):
        return type(self) == type(other) \
            and self.relation == other.relation \
            and self.args == other.args

class Proposition(Predicate):
    """A predicate that does not take terms."""
    def __init__(self, name: str):
        super().__init__(Relation(name, 0), [])

class Connective(NamedTuple):
    """
    A binary operator that takes
    two subformulas.
    """
    f0: 'Formula'
    f1: 'Formula'

    def __repr__(self):
        return f"{self.__class__.__name__}({self.f0}, {self.f1})"
    def __hash__(self):
        return hash((self.__class__.__name__, self.f0, self.f1))
    def __eq__(self, other):
        return type(self) == type(other) \
            and self.f0 == other.f0 \
            and self.f1 == other.f1

class And(Connective):
    """And Connective"""
class Or(Connective):
    """Or Connective"""
class Imp(Connective):
    """Implication Connective"""
class Iff(Connective):
    """Iff Connective"""

@dataclass
class Not:
    """Negation of a formula"""
    subformula: 'Formula'
    def __repr__(self):
        return f"Not({self.subformula})"
    def __hash__(self):
        return hash((self.__class__.__name__, self.subformula))
    def __eq__(self, other):
        return type(self) == type(other) \
            and self.subformula == other.subformula
    def __contains__(self, x):
        return x == self.subformula

Formula = Union[Predicate, Not, Connective, bool]
Valuation = Dict[Predicate, bool]

def prop_eval(formula: Formula, valuation: Optional[Valuation] = None) -> bool:
    """
    Evaluate a propositional formula given a
    valuation dictionary v mapping Propositions to booleans.
    """
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

    # Connective Case
    subformula0 = prop_eval(formula[0], valuation)
    subformula1 = prop_eval(formula[1], valuation)
    if isinstance(formula, And):
        return subformula0 and subformula1
    if isinstance(formula, Or):
        return subformula0 or subformula1
    if isinstance(formula, Imp):
        return not subformula0 or subformula1
    # Last case if Iff
    return subformula0 == subformula1

def atoms(formula: Formula) -> Set[Predicate]:
    """Returns a set of predicates in a formula."""
    if isinstance(formula, bool):
        return set()
    if isinstance(formula, Predicate):
        return {formula}
    if isinstance(formula, Not):
        return atoms(formula.subformula)
    # Otherwise it's a connective
    return atoms(formula[0]) | atoms(formula[1])

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

# TODO
def is_propositional_formula(formula: Formula) -> bool:
    """
    Returns whether or not a formula is
    a statement in propositional logic.
    TODO: Since only propositional logic is encoded,
    this is for now true
    """
    return True
