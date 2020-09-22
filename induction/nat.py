"""
The natural number module is responsible for defining
natural numbers or nats. It also contains a RewriteSystem
that can be used to simplify a nat.
"""
from copy import deepcopy
from typing import Optional
from algebra import Constant, Function, FuncTerm, Term, Variable
from rewrite import RewriteRule, RewriteSystem, normal

__all__ = ['zero', 'S', 'dec']

# Constants and Functions
zero = Constant("0", sort="nat")
S = Function("S", 1, domain_sort="nat", range_sort="nat")
dec = Function("dec", 1, domain_sort="nat", range_sort="nat")

# Rules
_n = Variable("n", "nat")
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
    if not isinstance(x, FuncTerm) or x.sort != 'nat':
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
    if not isinstance(x, FuncTerm) or x.sort != 'nat':
        raise ValueError("simplify function expects a nat.")
    if x == zero:
        return deepcopy(x)
    return normal(x, rules)
