from algebra import *
from .ac import *
from copy import deepcopy

class ParityFunction(Function):
    def __init__(self, symbol : str):
        super().__init__(symbol, 1)
    def __call__(self, x):
        if isinstance(x, FuncTerm) and isinstance(x.function, ParityFunction):
            return x.arguments[0]
        return FuncTerm(self, (x,))

class Group:
    def __init__(self, name : str, operation : AFunction, inv = None, identity_symbol = "e"):
        if not isinstance(operation, AFunction):
            raise ValueError("operation must be associative (AFunction)")
        self.name = name
        self.identity = GroupElement(self, identity_symbol)
        self.inv = ParityFunction(name + "_inv") if inv is None else inv
        self.op = operation

class GroupElement(GenericTerm):
    def __init__(self, g : Group, symbol : str):
        super().__init__(symbol)
        self.group = g
    def __hash__(self):
        return hash((self.group.name, self.symbol))
    def __eq__(self, x):
        return type(self) is type(x) and self.group == x.group and self.symbol == x.symbol
    def __mul__(self, x):
        if x == self.group.identity:
            return deepcopy(self)
        if self == self.group.identity:
            return deepcopy(x)
        if self.group.inv(self) == x:
            return deepcopy(self.group.identity)
        if self == self.group.inv(x):
            return deepcopy(self.group.identity)
        return self.group.op(self, x)
    def __rmul__(self, x):
        if x == self.group.identity:
            return deepcopy(self)
        if self == self.group.identity:
            return deepcopy(x)
        if self.group.inv(self) == x:
            return deepcopy(self.group.identity)
        if self == self.group.inv(x):
            return deepcopy(self.group.identity)
        return self.group.op(x, self)

class AbelianGroup(Group):
    def __init__(self, name : str, operation : ACFunction, inv = None):
        if not isinstance(operation, ACFunction):
            raise ValueError("operation must be associative and commutative (ACFunction)")
        super().__init__(name, operation, inv = inv)