from algebra import *
from .ac import *
from .groups import *
from copy import deepcopy

class Ring:
    def __init__(self, name : str, add_operation : ACFunction, mul_operation : AFunction):
        if not isinstance(mul_operation, AFunction):
            raise ValueError("multiplication must be associative (AFunction)")
        self.name = name
        self.group = AbelianGroup(name, add_operation, inv = Function(name + "_neg", 1))
        self.zero = RingZero(self)
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
        return self.ring == x.ring and self.symbol == x.symbol
    def __add__(self, x):
        return super().__mul__(x)
    def __mul__(self, x):
        return self.ring.mul(self, x)

class RingZero(RingElement, GroupIdentity):
    def __init__(self, r : Ring):
        GroupIdentity.__init__(self, r.group)
        RingElement.__init__(self, r, "0")
    def __mul__(self, x):
        return RingZero(self.ring)
    def __rmul__(self, x):
        return RingZero(self.ring)
    def __radd__(self, x):
        return GroupIdentity.__rmul__(self, x)
