"""
The natural number module is responsible for defining
natural numbers or nats. It also contains a RewriteSystem
that can be used to simplify a nat.
"""
from copy import deepcopy
from symcollab.algebra import Constant, Function, FuncTerm, Term, Variable
from symcollab.rewrite import RewriteRule, RewriteSystem
from .inductive import Inductive, TheorySystem
from .boolean import Boolean
# from .pair import Pair

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

## Parity Test

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

## Arithmetic Functions

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

## Comparison Functions

eq = Function("eq", 2, domain_sort=Nat.sort, range_sort=Boolean.sort)
Nat.define(
    eq,
    RewriteSystem({
        RewriteRule(eq(Nat.zero, Nat.zero), Boolean.trueb),
        RewriteRule(eq(Nat.zero, Nat.S(_m)), Boolean.falseb),
        RewriteRule(eq(Nat.S(_n), Nat.zero), Boolean.falseb),
        RewriteRule(eq(Nat.S(_n), Nat.S(_m)), eq(_n, _m))
    })
)

neq = Function("neq", 2, domain_sort=Nat.sort, range_sort=Boolean.sort)
Nat.define(
    neq,
    RewriteSystem({
        RewriteRule(neq(_n, _m), Boolean.neg(eq(_n, _m)))
    })
)

le = Function("le", 2, domain_sort=Nat.sort, range_sort=Boolean.sort)
Nat.define(
    le,
    RewriteSystem({
        RewriteRule(le(Nat.zero, Nat.S(_m)), Boolean.trueb),
        RewriteRule(le(Nat.S(_n), Nat.zero), Boolean.falseb),
        RewriteRule(le(Nat.S(_n), Nat.S(_m)), le(_n, _m))
    })
)

lt = Function("lt", 2, domain_sort=Nat.sort, range_sort=Boolean.sort)
Nat.define(
    lt,
    RewriteSystem({
        RewriteRule(lt(_n, _m), Boolean.andb(le(_n, _m), neq(_n, _m)))
    })
)

gt = Function("gt", 2, domain_sort=Nat.sort, range_sort=Boolean.sort)
Nat.define(
    gt,
    RewriteSystem({
        RewriteRule(gt(_n, _m), Boolean.neg(le(_n, _m)))
    })
)

ge = Function("ge", 2, domain_sort=Nat.sort, range_sort=Boolean.sort)
Nat.define(
    ge,
    RewriteSystem({
        RewriteRule(ge(_n, _m), Boolean.orb(gt(_n, _m), eq(_n, _m)))
    })
)

## Min/Max Functions

_min = Function("min", 2, domain_sort=Nat.sort, range_sort=Nat.sort)
Nat.define(
    _min,
    RewriteSystem({
        RewriteRule(_min(Nat.zero, _n), Nat.zero),
        RewriteRule(_min(_n, Nat.zero), Nat.zero),
        RewriteRule(_min(Nat.S(_n), Nat.S(_m)), Nat.S(_min(_n, _m)))
    })
)

_max = Function("max", 2, domain_sort=Nat.sort, range_sort=Nat.sort)
Nat.define(
    _max,
    RewriteSystem({
        RewriteRule(_max(Nat.zero, _n), _n),
        RewriteRule(_max(_n, Nat.zero), _n),
        RewriteRule(_max(Nat.S(_n), Nat.S(_m)), Nat.S(_max(_n, _m)))
    })
)

# TODO: Fix implementations below...
# _divmod = Function("divmod", 4, domain_sort=Nat.sort, range_sort=Pair.sort)
# quotient = Variable("q", sort=Nat.sort)
# neg_remainder = Variable("r", sort=Nat.sort)
# Nat.define(
#     _divmod,
#     RewriteSystem({
#         RewriteRule(_divmod(Nat.zero, _m, quotient, neg_remainder), Pair.pair(quotient, neg_remainder)),
#         RewriteRule(_divmod(Nat.S(_n), _m, quotient, Nat.zero), _divmod(_n, _m, Nat.S(quotient), _m)),
#         RewriteRule(_divmod(Nat.S(_n), _m, quotient, Nat.S(neg_remainder)), _divmod(_n, _m, quotient, neg_remainder))
#     })
# )

# div = Function("div", 2, domain_sort=Nat.sort, range_sort=Nat.sort)
# Nat.define(
#     div,
#     RewriteSystem({
#         RewriteRule(div(_n, Nat.zero), Nat.zero),
#         RewriteRule(div(_n, Nat.S(_m)), Pair.fst(_divmod(_n, _m, Nat.zero, _m)))
#     })
# )

# mod = Function("mod", 2, domain_sort=Nat.sort, range_sort=Nat.sort)
# Nat.define(
#     mod,
#     RewriteSystem({
#         RewriteRule(mod(_n, Nat.zero), Nat.zero),
#         RewriteRule(mod(_n, Nat.S(_m)), Nat.minus(_m, Pair.lst(_divmod(_n, _m, Nat.zero, _m))))
#     })
# )
