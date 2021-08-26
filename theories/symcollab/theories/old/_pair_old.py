"""Definition and properties for two-arity tuple."""
from symcollab.algebra import Function, Variable
from symcollab.rewrite import RewriteRule, RewriteSystem
from .inductive import TheorySystem, Inductive

@Inductive
class Pair(TheorySystem):
    pair = Function("pair", 2)

# Fix domain of pair to take anything
Pair.pair.domain_sort = None

# Variables for later rules
_a = Variable("a", sort=Pair.sort)
_b = Variable("b", sort=Pair.sort)

fst = Function("fst", 1, domain_sort=Pair.sort)
Pair.define(
    fst,
    RewriteSystem({
        RewriteRule(fst(Pair.pair(_a, _b)), _a),
    })
)

lst = Function("lst", 1, domain_sort=Pair.sort)
Pair.define(
    lst,
    RewriteSystem({
        RewriteRule(lst(Pair.pair(_a, _b)), _b),
    })
)
