"""Encoding of Predicate Logic"""
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, NamedTuple, List, Optional, Set, Union
from symcollab.algebra import Term, Variable

__all__ = [
    'Relation', 'Predicate', 'Proposition',
    'Connective', 'And', 'Or', 'Imp', 'Iff',
    'Not', 'ForAll', 'Exists', 'Formula', 'Valuation'
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
        assert all((isinstance(x, (Constant, Variable, Function, FuncTerm)) for x in args))
        return Predicate(self, args)

    def __hash__(self):
        return hash(("Relation", self.name, self.arity))

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
        return hash(("Predicate", self.relation, *self.args))
    def __repr__(self):
        if self.relation.arity == 0:
            return self.relation.name
        return f"{self.relation.name}({', '.join(map(repr, self.args))})"
    def __eq__(self, other):
        return type(self) == type(other) \
            and self.relation == other.relation \
            and self.args == other.args

class Proposition(Predicate):
    """A predicate that does not take terms."""
    def __init__(self, name: str):
        super().__init__(Relation(name, 0), [])

# TODO: Try to make this an Abstract Class
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
    def __hash__(self):
        return hash((self.__class__.__name__, self.subformula))
    def __repr__(self):
        return f"Not({self.subformula})"
    def __contains__(self, x):
        return x == self.subformula

@dataclass
class ForAll:
    bound_variable: Variable
    subformula: 'Formula'
    def __hash__(self):
        return hash((self.__class__.__name__, self.bound_variable, self.subformula))
    # TODO: Should I have __contains__ ?

class Exists:
    def __init__(self, bound_variable: Variable, subformula: 'Formula'):
        self.bound_variable = bound_variable
        self.subformula = subformula
    def __hash__(self):
        return hash((self.__class__.__name__, self.bound_variable, self.subformula))
    # TODO: Should I have __contains__ ?

Formula = Union[Predicate, Not, Connective, ForAll, Exists, bool]
Valuation = Dict[Predicate, bool]


###############################################3
#### Encoding of First-Order Logic below
#### Implementation subject to change

from copy import deepcopy
from functools import reduce
from typing import Any
from symcollab.algebra import Function, FuncTerm, \
    Constant, SubstituteTerm, get_vars

GroundTerm = Union[FuncTerm, Constant]
def is_ground(t: Term):
    """
    Returns whether or not a term is ground
    which means it has no Variables
    """
    if isinstance(t, Constant):
        return True
    if isinstance(t, Variable):
        return False
    result = True
    for ti in t.arguments:
        result = result or is_ground(ti)
    return result

TermValuation = Dict[Variable, GroundTerm]

def fvt(t: Term) -> Set[Variable]:
    """Returns the set of variables from a term."""
    return get_vars(t, unique=True)

# TODO: Need to check the free version
def vars_from_formula(formula: Formula, only_free = False) -> Set[Variable]:
    """
    Variables in a first order formula.
    """
    if isinstance(formula, bool):
        return set()

    if isinstance(formula, Predicate):
        if formula.relation.arity == 0:
            return set()
        if formula.relation.arity == 1:
            return fvt(formula.args[0])
        # Combine the fvt from all the terms in the predicate
        return set(reduce(lambda a, b: a | b, (fvt(t) for t in formula.args)))

    if isinstance(formula, Not):
        return vars_from_formula(formula.subformula)

    if isinstance(formula, Connective):
        return vars_from_formula(formula[0]) | vars_from_formula(formula[1])

    if isinstance(formula, (ForAll, Exists)):
        if not only_free:
            return {formula.bound_variable} | vars_from_formula(formula.subformula)
        return vars_from_formula(formula.subformula) - {formula.bound_variable}

    raise ValueError(f"Unexpected type {type(formula)}")

def fv(formula: Formula) -> Set[Variable]:
    """Returns a set of free variables in a formula."""
    return vars_from_formula(formula, True)

def subformulaapply(formula: Formula, sigma: SubstituteTerm):
    """Applies a substitution to a formula."""
    # Can't apply a substitution to a bool or Proposition
    if isinstance(formula, (bool, Proposition)):
        return formula

    if isinstance(formula, Predicate):
        # If the arity is zero, then it's a Proposition
        if formula.relation.arity == 0:
            return formula
        # Otherwise, apply the substitution to all
        # the terms in the predicate
        new_terms = [
            term * sigma
            for term in formula.args
        ]
        return formula.relation(*new_terms)

    if isinstance(formula, Connective):
        return formula.__class__(
            subformulaapply(formula[0], sigma),
            subformulaapply(formula[1], sigma)
        )
    if isinstance(formula, Not):
        return Not(subformulaapply(formula.subformula, sigma))

    if isinstance(formula, (ForAll, Exists)):
        # TODO: This is based on how Substitions are
        # currently handled. If we decide that its a bug
        # we'll have to rewrite this logic....
        if formula.bound_variable in sigma.range():
            new_bvar = _fresh_var_in_formula(formula)
            sigma.add(formula.bound_variable, new_bvar)
            return formula.__class__(
                new_bvar,
                subformulaapply(formula.subformula, sigma)
            )

        if formula.bound_Variable in sigma.domain():
            sigma.remove(formula.bound_variable)

        return formula.__class__(
            formula.bound_variable,
            subformulaapply(new_subform, sigma)
        )

    raise ValueError(f"Unexpected type: {type(formula)}.")

def _fresh_var_in_formula(formula: Formula):
    fresh_var = Variable("x")
    while fresh_var in vars_from_formula(formula):
        fresh_var = Variable(fresh_var.symbol + "'")
    return fresh_var
