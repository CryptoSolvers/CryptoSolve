"""
The Boolean module is responsible for defining
a symbolic bool (true/false) and properties
of them.
"""
from copy import deepcopy
from symcollab.algebra import Constant, Function, FuncTerm, Term, Variable
from symcollab.rewrite import RewriteRule, RewriteSystem
from .inductive import Inductive, TheorySystem

__all__ = ['Boolean']

@Inductive
class Boolean(TheorySystem):
    trueb = Constant("true")
    falseb = Constant("false")

    @classmethod
    def from_bool(cls, x: bool) -> Term:
        """Converts a bool to a Boolean."""
        return deepcopy(Boolean.trueb if x else Boolean.falseb)

    @classmethod
    def to_bool(cls, x: Term) -> bool:
        """Converts a Boolean to an bool."""
        if not isinstance(x, FuncTerm) or x != Boolean.trueb or x != Boolean.falseb:
            raise ValueError("to_bool function expects a simplified Boolean.")
        return x == Boolean.trueb


# Variables for later rules
_n = Variable("n", sort=Boolean.sort)
_m = Variable("m", sort=Boolean.sort)

# Negation
neg = Function("neg", 1, domain_sort=Boolean.sort, range_sort=Boolean.sort)
Boolean.define(
    neg,
    RewriteSystem({
        RewriteRule(neg(Boolean.trueb), Boolean.falseb),
        RewriteRule(neg(Boolean.falseb), Boolean.trueb)
    })
)

# Boolean And
andb = Function("andb", 2, domain_sort=Boolean.sort, range_sort=Boolean.sort)
Boolean.define(
    andb,
    RewriteSystem({
        RewriteRule(andb(Boolean.trueb, _n), _n),
        RewriteRule(andb(Boolean.falseb, _n), Boolean.falseb)
    })
)

# Boolean Or
orb = Function("orb", 2, domain_sort=Boolean.sort, range_sort=Boolean.sort)
Boolean.define(
    orb,
    RewriteSystem({
        RewriteRule(orb(Boolean.trueb, _n), Boolean.trueb),
        RewriteRule(orb(Boolean.falseb, _n), _n)
    })
)

# Boolean Exclusive-Or
xorb = Function("xorb", 2, domain_sort=Boolean.sort, range_sort=Boolean.sort)
Boolean.define(
    xorb,
    RewriteSystem({
        RewriteRule(xorb(Boolean.trueb, Boolean.trueb), Boolean.falseb),
        RewriteRule(xorb(Boolean.falseb, Boolean.falseb), Boolean.falseb),
        RewriteRule(xorb(Boolean.trueb, Boolean.falseb), Boolean.trueb),
        RewriteRule(xorb(Boolean.falseb, Boolean.trueb), Boolean.trueb)
    })
)

# Boolean Equals
eq = Function("eq", 2, domain_sort=Boolean.sort, range_sort=Boolean.sort)
Boolean.define(
    eq,
    RewriteSystem({
        RewriteRule(eq(Boolean.trueb, Boolean.trueb), Boolean.trueb),
        RewriteRule(eq(Boolean.falseb, Boolean.falseb), Boolean.trueb),
        RewriteRule(eq(Boolean.trueb, Boolean.falseb), Boolean.falseb),
        RewriteRule(eq(Boolean.falseb, Boolean.trueb), Boolean.falseb),
    })
)

# Boolean Not-Equals
neq = Function("neq", 2, domain_sort=Boolean.sort, range_sort=Boolean.sort)
Boolean.define(
    neq,
    RewriteSystem({
        RewriteRule(neq(_n, _m), neg(eq(_n, _m)))
    })
)
