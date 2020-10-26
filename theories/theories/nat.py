"""
The natural number module is responsible for defining
natural numbers or nats. It also contains a RewriteSystem
that can be used to simplify a nat.
"""
from copy import deepcopy
from algebra import Constant, Function, FuncTerm, Term, Variable
from rewrite import RewriteRule, RewriteSystem
from .inductive import Inductive, TheorySystem
from .boolean import Boolean

__all__ = ['Nat']

@Inductive
class Nat(TheorySystem):
    zero = Constant("0")
    S = Function("S", 1)

    @classmethod
    def from_int(cls, x: int) -> Term:
        """Converts an integer to a nat."""
        result = deepcopy(Nat.zero)
        for _ in range(x):
            result = Nat.S(result)
        return result

    @classmethod
    def to_int(cls, x: Term) -> int:
        """Converts a nat to an int."""
        if not isinstance(x, FuncTerm) or x.sort != Nat.sort:
            raise ValueError("to_int function expects a nat.")
        if x == Nat.zero:
            return 0
        if isinstance(x, FuncTerm) and x.function == Nat.S:
            return 1 + cls.to_int(x.arguments[0])
        raise ValueError("to_int: Only accepts signature {0, S}")

# Variables for later rules
_n = Variable("n", sort=Nat.sort)
_m = Variable("m", sort=Nat.sort)

# Decrement
dec = Function("dec", 1, domain_sort=Nat.sort, range_sort=Nat.sort)
Nat.define(
    dec,
    RewriteSystem({
        RewriteRule(dec(Nat.S(_n)), _n),
        RewriteRule(dec(Nat.zero), Nat.zero)
    })
)

even = Function("even", 1, domain_sort=Nat.sort, range_sort=Boolean.sort)
Nat.define(
    even,
    RewriteSystem({
        RewriteRule(even(Nat.zero), Boolean.trueb),
        RewriteRule(even(Nat.S(Nat.zero)), Boolean.falseb),
        RewriteRule(even(Nat.S(Nat.S(_n))), even(_n))
    })
)

odd = Function("odd", 1, domain_sort=Nat.sort, range_sort=Boolean.sort)
Nat.define(
    odd,
    RewriteSystem({
        RewriteRule(odd(_n), Boolean.neg(even(_n)))
    })
)

# Nat Equality Check
nat_eq = Function("nat_eq", 2, domain_sort=Nat.sort, range_sort=Boolean.sort)
Nat.define(
    nat_eq,
    RewriteSystem({
        RewriteRule(nat_eq(Nat.zero, Nat.zero), Boolean.trueb),
        RewriteRule(nat_eq(Nat.zero, Nat.S(_m)), Boolean.falseb),
        RewriteRule(nat_eq(Nat.S(_n), Nat.zero), Boolean.falseb),
        RewriteRule(nat_eq(Nat.S(_n), Nat.S(_m)), nat_eq(_n, _m))
    })
)

# Less than or equal to check
nat_le = Function("nat_le", 2, domain_sort=Nat.sort, range_sort=Boolean.sort)
Nat.define(
    nat_le,
    RewriteSystem({
        RewriteRule(nat_le(Nat.zero, Nat.S(_m)), Boolean.trueb),
        RewriteRule(nat_le(Nat.S(_n), Nat.zero), Boolean.falseb),
        RewriteRule(nat_le(Nat.S(_n), Nat.S(_m)), nat_le(_n, _m))
    })
)

plus = Function("plus", 2, domain_sort=Nat.sort, range_sort=Nat.sort)
Nat.define(
    plus,
    RewriteSystem({
        RewriteRule(plus(Nat.zero, _n), _n),
        RewriteRule(plus(Nat.S(_n), _m), Nat.S(plus(_n, _m)))
    })
)

minus = Function("minus", 2, domain_sort=Nat.sort, range_sort=Nat.sort)
Nat.define(
    minus,
    RewriteSystem({
        RewriteRule(minus(Nat.zero, _n), Nat.zero),
        RewriteRule(minus(_n, Nat.zero), _n),
        RewriteRule(minus(Nat.S(_n), Nat.S(_m)), minus(_n, _m))
    })
)

mult = Function("mult", 2, domain_sort=Nat.sort, range_sort=Nat.sort)
Nat.define(
    mult,
    RewriteSystem({
        RewriteRule(mult(Nat.zero, _m), Nat.zero),
        RewriteRule(mult(Nat.S(_n), _m), plus(_m, mult(_n, _m)))
    })
)

exp = Function("exp", 2, domain_sort=Nat.sort, range_sort=Nat.sort)
Nat.define(
    exp,
    RewriteSystem({
        RewriteRule(exp(_n, Nat.zero), Nat.S(Nat.zero)),
        RewriteRule(exp(_n, Nat.S(_m)), mult(_n, exp(_n, _m)))
    })
)


factorial = Function("factorial", 1, domain_sort=Nat.sort, range_sort=Nat.sort)
Nat.define(
    factorial,
    RewriteSystem({
        RewriteRule(factorial(Nat.zero), Nat.S(Nat.zero)),
        RewriteRule(factorial(Nat.S(_n)), mult(Nat.S(_n), factorial(_n)))
    })
)
