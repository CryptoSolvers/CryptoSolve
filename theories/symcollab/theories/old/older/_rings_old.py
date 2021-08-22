from symcollab.algebra import *
from .ac import *
from .groups import *
from copy import deepcopy
from symcollab.rewrite import *

# A ring R is an algebraic structure with the following properties:
# (1) R with addition is an Abelian Group
# (2) R is closed with respect to multiplication
# (3) Multiplication is associative
# (4) Multiplication distributes over addition
# To define a ring R with unity (R has a multiplicative identity) initialize unity_symbol to be a string
# Otherwise the ring will not have a unity
class Ring:
    def __init__(self, name : str, add_operation : ACFunction, mul_operation : AFunction, zero_symbol = "0", unity_symbol = None):
        if not isinstance(mul_operation, AFunction):
            raise ValueError("multiplication must be associative (AFunction)")
        self.name = name
        self.group = AbelianGroup(name, add_operation, inv_symbol = name + "_neg")
        self.unity = RingConstant(self, unity_symbol) if unity_symbol is not None else None
        self.set_zero(RingConstant(self, zero_symbol))
        self.neg = self.group.inv
        self.add = RingFunction(self, add_operation)
        self.mul = RingFunction(self, mul_operation)
        self.group.op = self.add # Turns GroupFunction into a RingFunction
    def __eq__(self, x):
        return type(self) is type(x) and self.name == x.name and self.add == x.add and self.mul == x.mul
    def __hash__(self):
        return hash(self.name)
    def has_unity(self):
        return self.unity is not None
    def set_zero(self, x):
        self.zero = x
        self.group.identity = x

class RingFunction(AFunction):
    def __init__(self, r : Ring, f : Function):
        super().__init__(f.symbol, f.arity)
        self.ring = r
        self.function = f
    def __call__(self, *args):
        term = self.function(*args)
        # Important for function calls that returns only a constant
        if not isinstance(term, FuncTerm) or term.function.arity == 0:
            return deepcopy(term)
        result = RingFuncTerm(self.ring, term)
        result.set_function(self)
        return result

def _left_distributivity(r : Ring, term):
    w = Variable("w")
    y = Variable("y")
    z = Variable("z")
    rule = RewriteRule(r.mul(w, r.add(y, z)), r.add(r.mul(w, y), r.mul(w, z)))
    return rule.apply(term)

def _right_distributivity(r : Ring,  term):
    w = Variable("w")
    y = Variable("y")
    z = Variable("z")
    rule = RewriteRule(r.mul(r.add(y, z), w), r.add(r.mul(y, w), r.mul(z, w)))
    return rule.apply(term)

# Applies both right distributivity and left distributivity rules
def _distributivity(r : Ring, term):
    return _left_distributivity(r, _right_distributivity(r, term))

# Class that describes an element of the ring.
# FuncTerms, Constants, and Variables all inherit from this group
# Addition is defined so you can add elements like a + b
# Multiplication is defined so that you can multiply elements like a * b
class RingElement(GroupElement):
    def __init__(self, r : Ring):
        GroupElement.__init__(self, r.group)
        self.ring = r
    # -a is the additive inverse of a
    def __neg__(self):
        return self.ring.neg(self)
    def __add__(self, x):
        result = super().__mul__(x)
        return self.ring.simplify_term(result) if hasattr(self.ring, 'simplify_term') else result
    def __radd__(self, x):
        result = super().__rmul__(x)
        return self.ring.simplify_term(result) if hasattr(self.ring, 'simplify_term') else result
    # a - b = a + (-b)
    def __sub__(self, x):
        result = self + (-x)
        return self.ring.simplify_term(result) if hasattr(self.ring, 'simplify_term') else result
    def __rsub__(self, x):
        result = self + (-x)
        return self.ring.simplify_term(result) if hasattr(self.ring, 'simplify_term') else result
    # Properties of multiplication return (True, result) if one matches otherwise (false, None)
    def _ringmulprops(self, x):
        if x == self.ring.zero or self == self.ring.zero:
            return (True, deepcopy(self.ring.zero))
        if self.ring.has_unity():
            if x == self.ring.unity:
                return (True, deepcopy(self))
            if self == self.ring.unity:
                return (True, deepcopy(x))
        if not self.ring.has_unity():
            if x == self.ring.unity:
                raise ValueError("The ring " + self.ring.name + " does not have a unity")
            if self == self.ring.unity:
                raise ValueError("The ring " + self.ring.name + " does not have a unity")
        return (False, None)
    def __mul__(self, x):
        # To get around the problem of syntax sharing with SubstituteTerms
        if isinstance(x, SubstituteTerm):
            return NotImplemented
        matched, term = self._ringmulprops(x)
        result = _distributivity(self.ring, self.ring.mul(self, x) if not matched else term)
        return self.ring.simplify_term(result) if hasattr(self.ring, 'simplify_term') else result
    def __rmul__(self, x):
        matched, term = self._ringmulprops(x)
        result = _distributivity(self.ring, self.ring.mul(x, self) if not matched else term)
        return self.ring.simplify_term(result) if hasattr(self.ring, 'simplify_term') else result
    def __truediv__(self, x):
        raise NotImplementedError("Rings do not have multiplicative inverses in general.")
    def __rtruediv__(self, x):
        raise NotImplementedError("Rings do not have multiplicative inverses in general.")

class RingVariable(RingElement, Variable):
    def __init__(self, r : Ring, symbol : str):
        RingElement.__init__(self, r)
        Variable.__init__(self, symbol)
    def __hash__(self):
        return hash((self.ring, self.symbol))
    def __eq__(self, x):
        return type(self) is type(x) and self.group == x.group and self.symbol == x.symbol

class RingFuncTerm(RingElement, ATerm):
    def __init__(self, r : Ring, a_term : ATerm):
        RingElement.__init__(self, r)
        FuncTerm.__init__(self, a_term.function, a_term.arguments)
        self.term = a_term
    def set_arguments(self, args):
        self.term.arguments = tuple(args)
        self.arguments = tuple(args)
    def set_function(self, function : Function):
        self.function = function
        self.term.function = function
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
