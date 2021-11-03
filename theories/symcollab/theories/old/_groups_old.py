"""
The groups module contains a class to create
generic groups with custom operations, inverses,
and identities.
"""
from symcollab.algebra import Constant, Function, Variable
from symcollab.rewrite import RewriteRule, RewriteSystem
from .inductive import Inductive, TheorySystem

__all__ = ['Group']

@Inductive
class Group(TheorySystem):
    """
    A group is a set G with an operation op that contain the
    closure and associative properties, as well as contains
    an identity and inverse element.
    """
    identity = Constant("e")
    op = Function("op", 2)
    inverse = Function("inv", 1)

_x = Variable("x", sort=Group.sort)
_y = Variable("y", sort=Group.sort)
_z = Variable("z", sort=Group.sort)
# From page 184 of Term Rewriting and All That
Group.rules = RewriteSystem({
    ## Associativity
    # (x * y) * z → x * (y * z)
    RewriteRule(Group.op(Group.op(_x, _y), _z), Group.op(_x, Group.op(_y, _z))),
    ## Identity Rules
    # 1 * x → x
    RewriteRule(Group.op(Group.identity, _x), _x),
    # x * 1 → x
    RewriteRule(Group.op(_x, Group.identity), _x),
    ## Inverse Rules
    # x * i(x) → 1
    RewriteRule(Group.op(_x, Group.inverse(_x)), Group.identity),
    # i(x) * x → 1
    RewriteRule(Group.op(Group.inverse(_x), _x), Group.identity),
    # i(1) → 1
    RewriteRule(Group.inverse(Group.identity), Group.identity),
    # i(i(x)) → x
    RewriteRule(Group.inverse(Group.inverse(_x)), _x),
    # i(x * y) → i(y) * i(x)
    RewriteRule(Group.inverse(Group.op(_x, _y)), Group.op(Group.inverse(_y), Group.inverse(_x))),
    ## Interplay between associativity and inverses
    # x * (i(x) * y) → y
    RewriteRule(Group.op(_x, Group.op(Group.inverse(_x), _y)), _y),
    # i(x) * (x * y) → y
    RewriteRule(Group.op(Group.inverse(_x), Group.op(_x, _y)), _y)
})
