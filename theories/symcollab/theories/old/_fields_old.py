"""
UNFINISHED
An implementation of Algebraic Fields. This module can use some rework
to utilize the sort attribute in the algebra module.

See nat.py for a more modern take of implementing a theory.
"""
from symcollab.algebra import Constant, Function, Term, Variable
from symcollab.rewrite import RewriteRule, RewriteSystem, normal
from .rings import Ring
from .inductive import Inductive, TheorySystem

__all__ = ['Field']

# TODO: Capture the commutative property of addition & multiplication
# TODO: Make sure zero is noninvertible

@Inductive
class Field(TheorySystem):
    """
    A field is a ring with every nonzero element
    having a multiplicative inverse.
    """
    add = Function("add", 2)
    mul = Function("mul", 2)
    negate = Function("neg", 1)
    inverse = Function("inv", 1)
    zero = Constant("0")
    unity = Constant("1")

_x = Variable("x", sort=Field.sort)
_y = Variable("y", sort=Field.sort)
# TODO: Fix symbols of Ring and Field rules
Field.rules = RewriteSystem(Ring.rules.rules | {
    ## One and Zero
    # 1 * 0 -> 0
    RewriteRule(Field.mul(Field.unity, Field.zero), Field.zero),
    # 0 * 1 -> 0
    RewriteRule(Field.mul(Field.zero, Field.unity), Field.zero),
    # 1 + 0 -> 1
    RewriteRule(Field.add(Field.unity, Field.zero), Field.unity),
    # 0 + 1 -> 1
    RewriteRule(Field.add(Field.zero, Field.unity), Field.unity),
    ## Unity Rules
    # 1 * x → x
    RewriteRule(Field.mul(Field.unity, _x), _x),
    # x * 1 → x
    RewriteRule(Field.mul(_x, Field.unity), _x),
    # -1 * x → -x
    RewriteRule(Field.mul(Field.negate(Field.unity), _x), Field.negate(_x)),
    # x * -1 → -x
    RewriteRule(Field.mul(_x, Field.negate(Field.unity)), Field.negate(_x)),
    # x * i(x) → 1
    RewriteRule(Field.mul(_x, Field.inverse(_x)), Field.unity),
    # i(x) * x → 1
    RewriteRule(Field.mul(Field.inverse(_x), _x), Field.unity),
    ## Inverse Rules
    # i(i(x)) → x
    RewriteRule(Field.inverse(Field.inverse(_x)), _x),
    # i(x * y) → i(y) * i(x)
    RewriteRule(Field.inverse(Field.mul(_x, _y)), Field.mul(Field.inverse(_y), Field.inverse(_x))),
    ## Interplay between associativity and inverses
    # x * (i(x) * y) → y
    RewriteRule(Field.mul(_x, Field.mul(Field.inverse(_x), _y)), _y),
    # i(x) * (x * y) → y
    RewriteRule(Field.mul(Field.inverse(_x), Field.mul(_x, _y)), _y)
})
