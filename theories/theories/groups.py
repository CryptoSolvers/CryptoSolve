from rewrite import *
from algebra import *
from copy import deepcopy

class Group:
    @staticmethod
    def create_rules(op : Function, inverse : Function, identity : Constant) -> Set[RewriteRule]:
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
    
    def __init__(self, op : Function, inverse : Function, identity : Constant):
        self.op = op
        self.inverse = inverse
        self.identity = identity
        self.rewrite_rules = Group.create_rules(op, inverse, identity)
    
    def normal(self, element : Term):
        return normal(element, self.rewrite_rules)


