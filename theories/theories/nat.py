"""
The natural number module is responsible for defining
natural numbers or nats. It also contains a RewriteSystem
that can be used to simplify a nat.
"""
from copy import deepcopy
from algebra import Constant, Function, FuncTerm, Term, Variable
from rewrite import RewriteRule, RewriteSystem
from .inductive import Inductive

__all__ = ['Nat']

@Inductive
class Nat:
    # Core Definition
    zero = Constant("0")
    S = Function("S", 1)

    # Unary Functions
    dec = Function("dec", 1)

    # Binary Functions
    plus = Function("plus", 2)
    minus = Function("minus", 2)
    mult = Function("mult", 2)
    exp = Function("exp", 2)

##
# Rules
##

# Variables for later rules
_n = Variable("n", sort=Nat.sort)
_m = Variable("m", sort=Nat.sort)

# Dec Rules
Nat.add_rules({
    RewriteRule(Nat.dec(Nat.S(_n)), _n),
    RewriteRule(Nat.dec(Nat.zero), Nat.zero)
})

# Plus Rules
Nat.add_rules({
    RewriteRule(Nat.plus(Nat.zero, _n), _n),
    RewriteRule(Nat.plus(Nat.S(_n), _m), Nat.S(Nat.plus(_n, _m)))
})

# Minus Rules
Nat.add_rules({
    RewriteRule(Nat.minus(Nat.zero, _n), Nat.zero),
    RewriteRule(Nat.minus(_n, Nat.zero), _n),
    RewriteRule(Nat.minus(Nat.S(_n), Nat.S(_m)), Nat.minus(_n, _m))
})

# Mult Rules
Nat.add_rules({
    RewriteRule(Nat.mult(Nat.zero, _m), Nat.zero),
    RewriteRule(Nat.mult(Nat.S(_n), _m), Nat.plus(_m, Nat.mult(_n, _m)))
})


# Exp Rules
Nat.add_rules({
    RewriteRule(Nat.exp(_n, Nat.zero), Nat.S(Nat.zero)),
    RewriteRule(Nat.exp(_n, Nat.S(_m)), Nat.mult(_n, Nat.exp(_n, _m)))
})


def from_int(x: int) -> Term:
    """Converts an integer to a nat."""
    result = deepcopy(Nat.zero)
    for _ in range(x):
        result = Nat.S(result)
    return result

def to_int(x: Term) -> int:
    """Converts a nat to an int."""
    if not isinstance(x, FuncTerm) or x.sort != Nat.sort:
        raise ValueError("to_int function expects a nat.")
    if x == Nat.zero:
        return 0
    if isinstance(x, FuncTerm) and x.function == Nat.S:
        return 1 + to_int(x.arguments[0])
    raise ValueError("to_int: Only accepts signature {0, S}")

setattr(Nat, 'from_int', from_int)
setattr(Nat, 'to_int', to_int)
