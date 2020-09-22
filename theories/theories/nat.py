"""
The natural number module is responsible for defining
natural numbers or nats. It also contains a RewriteSystem
that can be used to simplify a nat.
"""
from copy import deepcopy
from typing import Optional
from algebra import Constant, Function, FuncTerm, Sort, Term, Variable
from rewrite import RewriteRule, RewriteSystem, normal

__all__ = ['zero', 'S', 'dec', 'nat_sort']

# Constants and Functions
nat_sort = Sort("nat")
zero = Constant("0", sort=nat_sort)
S = Function("S", 1, domain_sort=nat_sort, range_sort=nat_sort)
dec = Function("dec", 1, domain_sort=nat_sort, range_sort=nat_sort)

# Rules
_n = Variable("n", sort=nat_sort)
dec_rule1 = RewriteRule(dec(S(_n)), _n)
dec_rule2 = RewriteRule(dec(zero), zero)
rules = RewriteSystem({dec_rule1, dec_rule2})

def from_int(x: int) -> Term:
    """Converts an integer to a nat."""
    result = deepcopy(zero)
    for _ in range(x):
        result = S(result)
    return result

def to_int(x: Term) -> int:
    """Converts a nat to an int."""
    if not isinstance(x, FuncTerm) or x.sort != nat_sort:
        raise ValueError("to_int function expects a nat.")
    if x == zero:
        return 0
    if isinstance(x, FuncTerm) and x.function == S:
        return 1 + to_int(x.arguments[0])
    raise ValueError("to_int: Only accepts signature {0, S}")

def simplify(x: Term) -> Optional[Term]:
    """
    Simplify a nat term using the convergent
    rewrite rules in the nat module.
    """
    if not isinstance(x, FuncTerm) or x.sort != nat_sort:
        raise ValueError("simplify function expects a nat.")
    if x == zero:
        return deepcopy(x)
    return normal(x, rules)
