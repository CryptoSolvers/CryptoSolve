"""
An implementation of Algebraic Groups. This module can use some rework
to utilize the sort attribute in the algebra module.

See nat.py for a more modern take of implementing a theory.
"""
from typing import Set
from algebra import Constant, Function, Term, Variable
from rewrite import RewriteRule, RewriteSystem, normal

__all__ = ['Group']

class Group:
    """
    A group is a set G with an operation op that contain the
    closure and associative properties, as well as contains
    an identity and inverse element.
    """
    @staticmethod
    def create_rules(op: Function, inverse: Function, identity: Constant) -> Set[RewriteRule]:
        """Create the set of rewrite rules that characterizes an algebraic group."""
        x = Variable("x") ; y = Variable("y") ; z = Variable("z")
        # From page 184 of Term Rewriting and All That
        return {
            ## Associativity
            # (x * y) * z → x * (y * z)
            RewriteRule(op(op(x, y), z), op(x, op(y, z))),
            ## Identity Rules
            # 1 * x → x
            RewriteRule(op(identity, x), x),
            # x * 1 → x
            RewriteRule(op(x, identity), x),
            ## Inverse Rules
            # x * i(x) → 1
            RewriteRule(op(x, inverse(x)), identity),
            # i(x) * x → 1
            RewriteRule(op(inverse(x), x), identity),
            # i(1) → 1
            RewriteRule(inverse(identity), identity),
            # i(i(x)) → x
            RewriteRule(inverse(inverse(x)), x),
            # i(x * y) → i(y) * i(x)
            RewriteRule(inverse(op(x, y)), op(inverse(y), inverse(x))),
            ## Interplay between associativity and inverses
            # x * (i(x) * y) → y
            RewriteRule(op(x, op(inverse(x), y)), y),
            # i(x) * (x * y) → y
            RewriteRule(op(inverse(x), op(x, y)), y)
        }

    def __init__(self, op: Function, inverse: Function, identity: Constant):
        self.op = op
        self.inverse = inverse
        self.identity = identity
        self.rewrite_rules = Group.create_rules(op, inverse, identity)

    def normal(self, element: Term):
        """Normal form of a group term."""
        return normal(element, RewriteSystem(self.rewrite_rules))
