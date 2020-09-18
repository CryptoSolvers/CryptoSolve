"""
Natural number module
"""
from copy import deepcopy
from algebra import Constant, Function, FuncTerm, Term, Variable
from rewrite import RewriteRule

__all__ = ['zero', 'S', 'from_int', 'to_int', 'dec']

zero = Constant("0", sort="nat")
S = Function("S", 1, domain_sort="nat", range_sort="nat")


def from_int(x: int):
    """Convert fron an int to a nat."""
    result = deepcopy(zero)
    for _ in range(x):
        result = S(result)
    return result

def to_int(x: Term):
    """Convert from a nat to an int."""
    if not isinstance(x, FuncTerm) or x.sort != 'nat':
        raise ValueError("to_int function expects a nat.")
    if x == zero:
        return 0
    if isinstance(x, FuncTerm) and x.function == S:
        return 1 + to_int(x.arguments[0])
    raise ValueError("to_int: Only accepts signature {0, S}")

_n = Variable("n", "nat")
# TODO: Figure out how i want to deal with dec...
dec = lambda x: RewriteRule(S(_n), _n).apply(x, '') 