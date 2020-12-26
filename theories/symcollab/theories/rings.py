"""
UNFINISHED
An implementation of Algebraic Rings. This module can use some rework
to utilize the sort attribute in the algebra module.

See nat.py for a more modern take of implementing a theory.
"""
from symcollab.algebra import Constant, Function, Variable
from symcollab.rewrite import RewriteRule, RewriteSystem
from .groups import Group
from .inductive import Inductive, TheorySystem

__all__ = ['Ring']

# TODO: Capture the commutative property of addition

@Inductive
class Ring(TheorySystem):
    """
    A ring is an abelian group with another binary
    operation that is associative, distributive over the
    abelian operation, and has an ientity element.
    """
    add = Function("add", 2)
    mul = Function("mul", 2)
    negate = Function("neg", 1)
    zero = Constant("0")

_x = Variable("x", sort=Group.sort)
_y = Variable("y", sort=Group.sort)
_z = Variable("z", sort=Group.sort)
# TODO: Make Group.rules.rules match what the function symbols are
Ring.rules = RewriteSystem(Group.rules.rules | {
    ## Associativity Rules
    # (x * y) * z → x * (y * z)
    RewriteRule(Ring.mul(Ring.mul(_x, _y), _z), Ring.mul(_x, Ring.mul(_y, _z))),
    ## Zero rules
    # 0 * x → 0
    RewriteRule(Ring.mul(Ring.zero, _x), Ring.zero),
    # x * 0 → 0
    RewriteRule(Ring.mul(_x, Ring.zero), Ring.zero),
    ## Distributivity rules
    # x * (y + z) → (x * y) + (x * z)
    RewriteRule(Ring.mul(_x, Ring.add(_y, _z)), Ring.add(Ring.mul(_x, _y), Ring.mul(_x, _z))),
    # (y + z) * x → (y * x) + (z * x)
    RewriteRule(Ring.mul(Ring.add(_y, _z), _x), Ring.add(Ring.mul(_y, _x), Ring.mul(_z, _x)))
})
