"""
Allows you to define sorts inductively.
In other words, constants and functions
under a sort class will have the sort
name associated with it.
"""
from copy import deepcopy
from typing import Dict, List, Optional
import functools
from symcollab.algebra import Constant, Function, FuncTerm, Sort, Term
from symcollab.rewrite import normal, RewriteRule, RewriteSystem

__all__ = ['Inductive', 'TheorySystem', 'system_from_sort']

class TheorySystem:
    """
    Contains a sort and the
    RewriteSystem that governs it.
    """
    sort: Sort = None
    rules: RewriteSystem = RewriteSystem(set())
    definitions: Dict[Function, RewriteSystem] = dict()

    @classmethod
    def simplify(cls, x: Term, bound: int = -1) -> Optional[Term]:
        """
        Simplify a term using the convergent
        rewrite rules known.
        """
        if not isinstance(x, FuncTerm):
            raise ValueError("simplify function expects a FuncTerm.")
        return normal(x, cls.rules, bound)[0]

    @classmethod
    def signature(cls) -> List[Term]:
        """List the signature of the system."""
        el = []
        for term in cls.__dict__.values():
            if not isinstance(term, (Constant, Function)):
                continue
            el.append(deepcopy(term))
        return el

    @classmethod
    def __len__(cls) -> int:
        """Return the number of elements."""
        return len(filter(lambda x: isinstance(x, Constant)), cls.__dict__.values())

    @classmethod
    def add_rule(cls, rule: RewriteRule) -> None:
        """Add a rule to the system."""
        if not isinstance(rule, RewriteRule):
            raise ValueError(f"add_rule expected a RewriteRule not a '{type(rule)}'.")
        cls.rules.append(rule)

    @classmethod
    def define(cls, function: Function, rules: RewriteSystem):
        """Define a function by a rewrite system."""
        setattr(cls, function.symbol, function)
        # TODO: Make sure RewriteSystem terminates
        # TODO: Does composition of terminating rewrite systems terminate?
        for rule in rules:
            cls.add_rule(rule)
        cls.definitions[function] = rules


def Inductive(cls=None):
    """
    Decorator that takes a TheorySystem and
    adds sorts to Constants and Functions defined.
    """
    if cls is not None and not issubclass(cls, TheorySystem):
        raise ValueError(
            "Inductive decorator only works \
             on classes that inherit TheorySystem."
        )

    @functools.wraps(cls)
    def wrap(cls):
        cls.sort = Sort(cls.__name__)
        cls.rules = deepcopy(cls.rules)
        cls.definitions = deepcopy(cls.definitions)
        for name, term in cls.__dict__.items():
            # Ignore private, already defined, and custom methods
            if '_' in name \
               or name in TheorySystem.__dict__ \
               or (callable(term) and not isinstance(term, Function)):
                continue

            if isinstance(term, Constant):
                if term.sort is not None and term.sort != cls.sort:
                    raise ValueError(
                        f"Constant {term} is of sort '{term.sort}' \
                          which is not the class name '{class_sort}'."
                    )

                setattr(
                    cls,
                    name,
                    Constant(term.symbol, sort=cls.sort)
                )

            elif isinstance(term, Function):
                if term.domain_sort is not None and term.domain_sort != cls.sort:
                    raise ValueError(
                        f"Function {term} has the domain sort \
                          set to '{term.domain_sort}' \
                          which is not the class name '{class_sort}'."
                    )

                range_sort = cls.sort if term.range_sort is None else term.range_sort
                setattr(
                    cls,
                    name,
                    Function(
                        term.symbol,
                        term.arity,
                        domain_sort=cls.sort,
                        range_sort=range_sort
                    )
                )

            else:
                raise ValueError(
                    f"Variable '{name}' is of invalid type \
                      '{type(term)}' inside an inductive class. (Constant, Function)"
                )

        _system_sort_map[cls.sort] = cls
        return cls

    # Called as decorator
    if cls is None:
        return wrap

    # Called as function
    return wrap(cls)

_system_sort_map: Dict[Sort, TheorySystem] = dict()

def system_from_sort(s: Sort) -> Optional[TheorySystem]:
    """Obtain a TheorySystem from a sort."""
    return _system_sort_map.get(s)
