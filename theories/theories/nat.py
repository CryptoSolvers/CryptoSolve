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

# Uniary Functions
S = Function("S", 1, domain_sort=nat_sort, range_sort=nat_sort)
dec = Function("dec", 1, domain_sort=nat_sort, range_sort=nat_sort)

# Binary Functions
plus = Function("plus", 2, domain_sort=nat_sort, range_sort=nat_sort)
minus = Function("minus", 2, domain_sort=nat_sort, range_sort=nat_sort)
mult = Function("mult", 2, domain_sort=nat_sort, range_sort=nat_sort)
exp = Function("exp", 2, domain_sort=nat_sort, range_sort=nat_sort)

# Rules
_n = Variable("n", sort=nat_sort)
_m = Variable("m", sort=nat_sort)

dec_rule1 = RewriteRule(dec(S(_n)), _n)
dec_rule2 = RewriteRule(dec(zero), zero)

plus_rule1 = RewriteRule(plus(zero, _n), _n)
plus_rule2 = RewriteRule(plus(S(_n), _m), S(plus(_n, _m)))

minus_rule1 = RewriteRule(minus(zero, _n), zero)
minus_rule2 = RewriteRule(minus(_n, zero), _n)
minus_rule3 = RewriteRule(minus(S(_n), S(_m)), minus(_n, _m))

mult_rule1 = RewriteRule(mult(zero, _m), zero)
mult_rule2 = RewriteRule(mult(S(_n), _m), plus(_m, mult(_n, _m)))

exp_rule1 = RewriteRule(exp(_n, zero), S(zero))
exp_rule2 = RewriteRule(exp(_n, S(_m)), mult(_n, exp(_n, _m)))

rules = RewriteSystem({
    dec_rule1, dec_rule2,
    plus_rule1, plus_rule2,
    minus_rule1, minus_rule2, minus_rule3,
    mult_rule1, mult_rule2,
    exp_rule1, exp_rule2
})

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
