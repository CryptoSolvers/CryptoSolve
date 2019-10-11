from algebra import *
from .ac import *
from .rings import *
from copy import deepcopy

BoolRingAdd = ACFunction("bool_add", 2)
BoolRingMul = ACFunction("bool_mul", 2)
BooleanRing = Ring("BooleanRing", BoolRingAdd, BoolRingMul)

class BoolRingFunction(Function):
    def __init__(self, r : Ring, f : Function):
        super().__init__(f.symbol, f.arity)
        self.ring = r
        self.function = f
    def __call__(self, *args):
        return RingFuncTerm(self.ring, self.function(*args))


def simplify_boolean_term(term : Term):
    if not isinstance(term, FuncTerm) or term.function not in [BoolRingMul, BoolRingAdd]:
        return deepcopy(term)
    args = term.flatten()
    new_args = []
    for arg in args:
        new_args.append(simplify_boolean_term(arg))
    if term.function == BoolRingMul:
        # Apply x * x -> x
        # [TODO] Ensure this is an appropriate technique by confirming that * is commutative
        new_args = list(set(new_args))
    elif term.function == BoolRingAdd:
        # Apply x + x -> 0
        var_constant_counts = Counter(new_args)
        new_args = []
        for t, count in var_constant_counts.items():
            if count % 2 == 1:
                new_args += [t]
    if len(new_args) > 1:
        term = term.function(*new_args)
    elif len(new_args) == 1:
        term = new_args[0]
    else:
        term = BooleanRing.zero
    return term

# Addition and multiplication are AC
class BooleanRingElement(RingElement):
    def __init__(self, symbol):
        RingElement.__init__(self, BooleanRing)
    # x + x = 0
    def __add__(self, x):
        if self == x:
            return deepcopy(self.ring.zero)
        # x = simplify_boolean_term(x)
        return super().__add__(x)
    def __radd__(self, x):
        if self == x:
            return deepcopy(self.ring.zero)
        x = simplify_boolean_term(x)
        return super().__radd__(x)
    # x * x = x
    def __mul__(self, x):
        if self == x:
            return deepcopy(x)
        x = simplify_boolean_term(x)
        return super().__mul__(x)
    def __rmul__(self, x):
        if self == x:
            return deepcopy(x)
        x = simplify_boolean_term(x)
        return super().__rmul__(x)