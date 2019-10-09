from algebra import *
from .ac import *
from .groups import *
from copy import deepcopy
from rewrite import *

class Ring:
    def __init__(self, name : str, add_operation : ACFunction, mul_operation : AFunction, zero_symbol = "0"):
        if not isinstance(mul_operation, AFunction):
            raise ValueError("multiplication must be associative (AFunction)")
        self.name = name
        self.group = AbelianGroup(name, add_operation, inv = ParityFunction(name + "_neg"))
        self.zero = RingElement(self, zero_symbol)
        self.group.identity = self.zero
        self.neg = self.group.inv
        self.add = add_operation
        self.mul = mul_operation

class RingElement(GroupElement):
    def __init__(self, r : Ring, symbol : str):
        GroupElement.__init__(self, r.group, symbol)
        self.ring = r
    def __hash__(self):
        return hash((self.ring.name, self.symbol))
    def __eq__(self, x):
        return type(self) is type(x) and self.ring == x.ring and self.symbol == x.symbol
    def __add__(self, x):
        return super().__mul__(x)
    def __radd__(self, x):
        return super().__rmul__(x)
    # Properties of multiplication return (True, result) if one matches otherwise (false, None)
    def _mulprops(self, x):
        if x == self.ring.zero or self == self.ring.zero:
            return (True, deepcopy(self.ring.zero))
        # # Setting up variables for distribution rules
        # w = Variable("w")
        # y = Variable("y")
        # z = Variable("z")
        # mul = Function(self.ring.mul.symbol, self.ring.mul.arity)
        # add = Function(self.ring.add.symbol, self.ring.add.arity)
        # # Left Distributivity
        # r = RewriteRule(mul(w, add(y, z)), add(mul(w, y), mul(w, z)))
        # new_x = r.apply(x)
        # if new_x is not x:
        #     return (True, new_x)
        # # Right Distributivity
        # r = RewriteRule(mul(add(y, z), w), add(mul(y, w), mul(z, w)))
        # new_x = r.apply(x)
        # if new_x is not x:
        #     return (True, new_x)
        return (False, None)
    def __mul__(self, x):
        matched, term = self._mulprops(x)
        return self.ring.mul(self, x) if not matched else term
    def __rmul__(self, x):
        matched, term = self._mulprops(x)
        return self.ring.mul(x, self) if not matched else term
