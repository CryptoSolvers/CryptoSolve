from rewrite import *
from algebra import *
from copy import deepcopy
from .groups import Group

# TODO: Capture the commutative property of addition

class Ring:
    @staticmethod
    def create_rules(add : Function, mul : Function, negation : Function, zero : Constant):
        x = Variable("x") ; y = Variable("y") ; z = Variable("z")
        # Union Group rules and new ring rules
        return Group.create_rules(add, negation, zero) | {
            ## Associativity Rules
            # (x * y) * z → x * (y * z)
            RewriteRule(mul(mul(x, y), z), mul(x, mul(y, z))),
            ## Zero rules
            # 0 * x → 0
            RewriteRule(mul(zero, x), zero),
            # x * 0 → 0
            RewriteRule(mul(x, zero), zero),
            ## Distributivity rules
            # x * (y + z) → (x * y) + (x * z)
            RewriteRule(mul(x, add(y, z)), add(mul(x, y), mul(x, z))),
            # (y + z) * x → (y * x) + (z * x)
            RewriteRule(mul(add(y, z), x), add(mul(y, x), mul(z, x)))
        }
    
    def __init__(self, add : Function, mul : Function, negation : Function, zero : Constant):
        self.add = add
        self.mul = mul
        self.negation = negation
        self.zero = zero
        self.rewrite_rules = Ring.create_rules(add, mul, negation, zero)
    
    def normal(self, element : Term):
        return normal(element, self.rewrite_rules)


