"""
Allows you to define sorts inductively.
In other words, constants and functions
under a sort class will have the sort
name associated with it.
"""
from copy import deepcopy
from typing import List, Optional, Set
import functools
from algebra import Constant, Function, FuncTerm, Sort, Term
from rewrite import normal, RewriteRule, RewriteSystem

__all__ = ['Inductive']


def simplify(cls, x: Term) -> Optional[Term]:
    """
    Simplify a term using the convergent
    rewrite rules in the inductive module.
    """
    if not isinstance(x, FuncTerm) or x.sort != cls.sort:
        raise ValueError(f"simplify function expects a {cls.sort}.")
    return normal(x, cls.rules)

def add_rule(cls, rule: RewriteRule) -> None:
    """
    Add a rule into the inductive definition.
    """
    if not isinstance(rule, RewriteRule):
        raise ValueError(f"add_rule expected a RewriteRule not a '{type(rule)}'.")
    cls.rules.append(rule)

def add_rules(cls, rules: Set[RewriteRule]) -> None:
    """
    Add a set of rules into the inductive definition.
    """
    if not isinstance(rules, set):
        raise ValueError(f"add_rules expected a set of RewriteRule not '{type(rules)}'.")
    for rule in rules:
        add_rule(cls, rule)

def elements(cls) -> List[Term]:
    """List the elements of the Inductive definition."""
    el = []
    for term in cls.__dict__.values():
        if not isinstance(term, (Constant, Function)):
            continue
        el.append(deepcopy(term))
    return el

def length(cls) -> int:
    """Return the length of the number of elements."""
    return len(elements(cls))


def Inductive(cls=None):
    """
    Decorator that makes a class a sort definition.
    It adds the class name as the sort parameter
    to any constant or function defined.
    """
    @functools.wraps(cls)
    def wrap(cls):
        class_sort = Sort(cls.__name__)
        rules = RewriteSystem({})
        for name, term in cls.__dict__.items():
            # Ignore private/dunder methods
            if '_' in name:
                continue


            if isinstance(term, Constant):
                if term.sort is not None and term.sort != class_sort:
                    raise ValueError(
                        f"Constant {term} is of sort '{term.sort}' \
                          which is not the class name '{class_sort}'."
                    )

                setattr(
                    cls,
                    name,
                    Constant(term.symbol, sort=class_sort)
                )

            elif isinstance(term, Function):
                if term.domain_sort is not None and term.domain_sort != class_sort:
                    raise ValueError(
                        f"Function {term} has the domain sort \
                          set to '{term.domain_sort}' \
                          which is not the class name '{class_sort}'."
                    )

                range_sort = class_sort if term.range_sort is None else term.range_sort
                setattr(
                    cls,
                    name,
                    Function(
                        term.symbol,
                        term.arity,
                        domain_sort=class_sort,
                        range_sort=range_sort
                    )
                )

            elif isinstance(term, RewriteRule):
                rules.append(term)

            else:
                raise ValueError(
                    f"Variable '{name}' is of invalid type \
                      '{type(term)}' inside an inductive class. (Constant, Function, RewriteRule)"
                )

        setattr(cls, 'sort', class_sort)
        setattr(cls, 'rules', rules)
        setattr(cls, 'elements', functools.partial(elements, cls))
        setattr(cls, 'length', functools.partial(length, cls))
        setattr(cls, 'add_rule', functools.partial(add_rule, cls))
        setattr(cls, 'simplify', functools.partial(simplify, cls))

        return cls

    # Called as decorator
    if cls is None:
        return wrap

    # Called as function
    return wrap(cls)
