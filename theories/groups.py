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
        self.identity = GroupConstant(self, identity_symbol)
        self.inv = ParityFunction(name + "_inv") if inv is None else inv
        self.op = GroupFunction(self, operation)
    def __hash__(self):
        return hash(self.name)

class GroupFunction(Function):
    def __init__(self, g : Group, f : Function):
        super().__init__(f.symbol, f.arity)
        self.group = g
        self.function = f
    def __call__(self, *args):
        return GroupFuncTerm(self.group, self.function(*args))

def groupTermToTerm(term):
    if isinstance(term, GroupConstant):
        return Constant(term.symbol)
    elif isinstance(term, GroupVariable):
        return Variable(term.symbol)
    elif isinstance(term, GroupFuncTerm):
        term.arguments = list(term.arguments)
        for i, t in enumerate(term.arguments):
            term.arguments[i] = groupTermToTerm(t)
        term.arguments = tuple(term.arguments)
        return FuncTerm(term.function, term.arguments)
    return deepcopy(term)

def termToGroupTerm(g : Group, term):
    if isinstance(term, Constant):
        return GroupConstant(g, term.symbol)
    elif isinstance(term, Variable):
        return GroupVariable(g, term.symbol)
    else: # Assuming FuncTerm...
        assert isinstance(term, FuncTerm)
        term.arguments = list(term.arguments)
        for i, t in enumerate(term.arguments):
            term.arguments[i] = termToGroupTerm(g, t)
        term.arguments = tuple(term.arguments)
        return GroupFuncTerm(g, term)


class GroupElement:
    def __init__(self, g : Group):
        self.group = g
    # Properties of multiplication return (True, result) if one matches otherwise (false, None)
    def _groupmulprops(self, x):
        if x == self.group.identity:
            return (True, deepcopy(self))
        if self == self.group.identity:
            return (True, deepcopy(x))
        if self.group.inv(self) == x or self == self.group.inv(x):
            return (True, deepcopy(self.group.identity))
        return (False, None)
    def __mul__(self, x):
        matched, term = self._groupmulprops(x)
        return self.group.op(self, x) if not matched else term
    def __rmul__(self, x):
        matched, term = self._groupmulprops(x)
        return self.group.op(x, self) if not matched else term



class GroupVariable(GroupElement, Variable):
    def __init__(self, g : Group, symbol : str):
        GroupElement.__init__(self, g)
        Variable.__init__(self, symbol)
    def __hash__(self):
        return hash((self.group, self.symbol))
    def __eq__(self, x):
        return type(self) is type(x) and self.group == x.group and self.symbol == x.symbol

class GroupFuncTerm(GroupElement, FuncTerm):
    def __init__(self, g : Group, a_term : ATerm):
        GroupElement.__init__(self, g)
        FuncTerm.__init__(self, a_term.function, a_term.arguments)
        self.term = a_term
    def __hash__(self):
        return hash((self.group, self.term))
    def __repr__(self):
        return repr(self.term)
    def __str__(self):
        return str(self.term)
    def __eq__(self, x):
        return type(self) is type(x) and self.group == x.group and self.term == x.term

class GroupConstant(GroupElement, Constant):
    def __init__(self, g : Group, symbol : str):
        GroupElement.__init__(self, g)
        Constant.__init__(self, symbol)
    def __hash__(self):
        return hash((self.group, self.symbol))
    def __eq__(self, x):
        return type(self) is type(x) and self.group == x.group and self.symbol == x.symbol

class AbelianGroup(Group):
    def __init__(self, name : str, operation : ACFunction, inv = None):
        if not isinstance(operation, ACFunction):
            raise ValueError("operation must be associative and commutative (ACFunction)")
        super().__init__(name, operation, inv = inv)