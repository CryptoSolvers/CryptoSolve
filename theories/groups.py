from algebra import *
from .ac import *



class Group:
    def __init__(self, name : str, operation : AFunction, inv = None):
        if not isinstance(operation, AFunction):
            raise ValueError("operation must be associative (AFunction)")
        self.name = name
        self.identity = GroupIdentity(self)
        self.inv = Function(name + "_inv", 1) if inv is None else inv
        self.op = operation

class GroupElement(GenericTerm):
    def __init__(self, g : Group, symbol : str):
        super().__init__(symbol)
        self.group = g
    def __hash__(self):
        return hash((self.group.name, self.symbol))
    def __eq__(self, x):
        return self.group == x.group and self.symbol == x.symbol
    def __mul__(self, x):
        return self.group.op(self, x)

class GroupIdentity(GroupElement):
    def __init__(self, g : Group):
        super().__init__(g, "e")
    def __mul__(self, x):
        return x
    def __rmul__(self, x):
        return x

class AbelianGroup(Group):
    def __init__(self, name : str, operation : ACFunction, inv = None):
        if not isinstance(operation, ACFunction):
            raise ValueError("operation must be associative and commutative (ACFunction)")
        super().__init__(name, operation, inv = inv)