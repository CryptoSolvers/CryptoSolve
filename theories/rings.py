from algebra import *
from .ac import *
from .groups import *
from copy import deepcopy

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
    def __mul__(self, x):
        if x == self.ring.zero or self == self.ring.zero:
            return deepcopy(self.ring.zero)
        return self.ring.mul(self, x)
    def __rmul__(self, x):
        if x == self.ring.zero or self == self.ring.zero:
            return deepcopy(self.ring.zero)
        return self.ring.mul(x, self)
