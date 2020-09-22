"""
The groups module contains a class to create
generic groups with custom operations, inverses,
and identities.
"""
from typing import Set
from algebra import Constant, Function, FuncTerm, Sort, Term, Variable
from rewrite import RewriteRule, RewriteSystem, normal

__all__ = ['Group']

class Group:
    """
    A group is a set G with an operation op that contain the
    closure and associative properties, as well as contains
    an identity and inverse element.
    """
    @staticmethod
    def create_rules(op: Function, inverse: Function, identity: Constant, sort: Sort) -> Set[RewriteRule]:
        """Create the set of rewrite rules that characterizes an algebraic group."""
        x = Variable("x", sort=sort)
        y = Variable("y", sort=sort)
        z = Variable("z", sort=sort)
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

    def __init__(self, op: Function, inverse: Function, identity: Constant, sort: Sort):
        # Both domain and range sort must be of the specified sort due to closure properties
        assert op.domain_sort == sort
        assert op.range_sort == sort
        assert inverse.domain_sort == sort
        assert inverse.range_sort == sort
        # Identity must be of the specified sort
        assert identity.sort == sort
        # op must be a binary function
        assert op.arity == 2
        # inverse must be a single argument function
        assert inverse.arity == 1
        self.op = op
        self.inverse = inverse
        self.identity = identity
        self.sort = sort
        self.rewrite_rules = Group.create_rules(op, inverse, identity, sort)

    def simplify(self, element: Term):
        """Normal form of a group term."""
        if not isinstance(element, FuncTerm) or element.sort != self.sort:
            raise ValueError(f"simplify function expects a {self.sort}.")
        return normal(element, RewriteSystem(self.rewrite_rules))
