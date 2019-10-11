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
        self.zero = RingConstant(self, zero_symbol)
        self.group.identity = self.zero
        self.neg = self.group.inv
        self.add = RingFunction(self, add_operation)
        self.mul = RingFunction(self, mul_operation)
    def __eq__(self, x):
        return type(self) is type(x) and self.name == x.name and self.add == x.add and self.mul == x.mul
    def __hash__(self):
        return hash(self.name)

class RingFunction(Function):
    def __init__(self, r : Ring, f : Function):
        super().__init__(f.symbol, f.arity)
        self.ring = r
        self.function = f
    def __call__(self, *args):
        return RingFuncTerm(self.ring, self.function(*args))

def ringTermToTerm(term):
    if isinstance(term, RingConstant) or isinstance(term, GroupConstant):
        return Constant(term.symbol)
    elif isinstance(term, RingVariable) or isinstance(term, GroupVariable):
        return Variable(term.symbol)
    elif isinstance(term, RingFuncTerm) or isinstance(term, GroupFuncTerm):
        term.arguments = list(term.arguments)
        for i, t in enumerate(term.arguments):
            term.arguments[i] = ringTermToTerm(t)
        term.arguments = tuple(term.arguments)
        return FuncTerm(term.function, term.arguments)
    return deepcopy(term)

def termToRingTerm(r : Ring, term):
    if isinstance(term, Constant):
        return RingConstant(r, term.symbol)
    elif isinstance(term, Variable):
        return RingVariable(r, term.symbol)
    else: # Assuming FuncTerm...
        assert isinstance(term, FuncTerm)
        term.arguments = list(term.arguments)
        for i, t in enumerate(term.arguments):
            term.arguments[i] = termToRingTerm(r, t)
        term.arguments = tuple(term.arguments)
        return RingFuncTerm(r, term)

def _left_distributivity(r : Ring, add : ACFunction, mul : AFunction, term):
    # Setting up variables for distribution rules
    w = Variable("w")
    y = Variable("y")
    z = Variable("z")
    mul = Function(mul.symbol, mul.arity)
    add = Function(add.symbol, add.arity)
    # Left Distributivity
    rule = RewriteRule(mul(w, add(y, z)), add(mul(w, y), mul(w, z)))
    normal_term = ringTermToTerm(term)
    return termToRingTerm(r, rule.apply(normal_term))

def _right_distributivity(r : Ring, add : ACFunction, mul : AFunction, term):
    # Setting up variables for distribution rules
    w = Variable("w")
    y = Variable("y")
    z = Variable("z")
    mul = Function(mul.symbol, mul.arity)
    add = Function(add.symbol, add.arity)
    # Left Distributivity
    rule = RewriteRule(mul(add(y, z), w), add(mul(y, w), mul(z, w)))
    normal_term = ringTermToTerm(term)
    return termToRingTerm(r, rule.apply(normal_term))

def _distributivity(r : Ring, add : ACFunction, mul : ACFunction, term):
    return _left_distributivity(r, add, mul, _right_distributivity(r, add, mul, term))

class RingElement(GroupElement):
    def __init__(self, r : Ring):
        GroupElement.__init__(self, r.group)
        self.ring = r
    def __add__(self, x):
        return termToRingTerm(self.ring, super().__mul__(x))
    def __radd__(self, x):
        return termToRingTerm(self.ring, super().__rmul__(x))
    # Properties of multiplication return (True, result) if one matches otherwise (false, None)
    def _ringmulprops(self, x):
        if x == self.ring.zero or self == self.ring.zero:
            return (True, deepcopy(self.ring.zero))
        return (False, None)
    def __mul__(self, x):
        matched, term = self._ringmulprops(x)
        return _distributivity(self.ring, self.ring.add, self.ring.mul,
                    self.ring.mul(self, x) if not matched else term)
    def __rmul__(self, x):
        matched, term = self._ringmulprops(x)
        return _distributivity(self.ring, self.ring.add, self.ring.mul,
                    self.ring.mul(x, self) if not matched else term)

class RingVariable(RingElement, Variable):
    def __init__(self, r : Ring, symbol : str):
        RingElement.__init__(self, r)
        Variable.__init__(self, symbol)
    def __hash__(self):
        return hash((self.ring, self.symbol))
    def __eq__(self, x):
        return type(self) is type(x) and self.group == x.group and self.symbol == x.symbol

class RingFuncTerm(RingElement, FuncTerm):
    def __init__(self, r : Ring, a_term : ATerm):
        RingElement.__init__(self, r)
        FuncTerm.__init__(self, a_term.function, a_term.arguments)
        self.term = a_term
    def __hash__(self):
        return hash((self.ring, self.term))
    def __eq__(self, x):
        return type(self) is type(x) and self.ring == x.ring and self.term == x.term
    def __repr__(self):
        return repr(self.term)
    def __str__(self):
        return str(self.term)

class RingConstant(RingElement, Constant):
    def __init__(self, r : Ring, symbol : str):
        RingElement.__init__(self, r)
        Constant.__init__(self, symbol)
    def __hash__(self):
        return hash((self.ring.name, self.symbol))
    def __eq__(self, x):
        return type(self) is type(x) and self.ring == x.ring and self.symbol == x.symbol
