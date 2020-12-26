from symcollab.algebra import *
from .ac import *
from .rings import *
from copy import deepcopy

# A field is a commutative (multiplication is commutative) ring with unity 
# where every nonzero element is invertible (has an inverse)
class Field(Ring):
    def __init__(self, name : str, add_operation : ACFunction, mul_operation : AFunction, zero_symbol = "0", unity_symbol = "1", mul_inv_symbol = None):
        if not isinstance(mul_operation, CFunction):
            raise ValueError("Multiplication operation must be both associative and commutative")
        super().__init__(name, add_operation, mul_operation, zero_symbol = zero_symbol, unity_symbol = unity_symbol)
        self.set_zero(FieldConstant(self, zero_symbol))
        self.unity = FieldConstant(self, unity_symbol)
        self.add = FieldFunction(self, add_operation)
        self.mul = FieldFunction(self, mul_operation)
        self.group.op = self.add # Turns GroupFunction into a FieldFunction
        self.inv = FieldInverseFunction(self, name + "_inv" if mul_inv_symbol is None else mul_inv_symbol)

class FieldInverseFunction(Function):
    def __init__(self, f : Field, symbol : str):
        super().__init__(symbol, 1)
        self.field = f
    def __call__(self, x):
        if x == self.field.zero:
            raise ValueError("Cannot take the multiplicative inverse of zero")
        if isinstance(x, FuncTerm) and isinstance(x.function, FieldInverseFunction):
            return x.arguments[0]
        return FuncTerm(self, (x,))

class FieldFunction(ACFunction):
    def __init__(self, f : Field, fn : Function):
        super().__init__(fn.symbol, fn.arity)
        self.field = f
        self.function = fn
    def __call__(self, *args):
        term = self.function(*args)
        # Important for function calls that returns only a constant
        if not isinstance(term, FuncTerm) or term.function.arity == 0:
            return deepcopy(term)
        result = FieldFuncTerm(self.field, term)
        result.set_function(self)
        return result


# Class that describes an element of the field inherits the ring element.
# Mainly allows for multiplicative inverses
class FieldElement(RingElement):
    def __init__(self, r : Ring):
        RingElement.__init__(self, r)
        # Properties of multiplication return (True, result) if one matches otherwise (false, None)
    def _ringmulprops(self, x):
        if self == self.ring.inv(x) or x == self.ring.inv(self):
            return (True, deepcopy(self.ring.unity))
        return super()._ringmulprops(x)
    def __truediv__(self, x):
        return self.__mul__(self.ring.inv(x))
    def __rtruediv__(self, x):
        return self.__rmul__(self.ring.inv(x))

class FieldVariable(RingVariable, FieldElement):
    def __init__(self, r : Ring, symbol : str):
        RingVariable.__init__(self, r, symbol)
        FieldElement.__init__(self, r)
    def __hash__(self):
        return hash((self.ring, self.symbol))
    def __eq__(self, x):
        return type(self) is type(x) and self.group == x.group and self.symbol == x.symbol

class FieldFuncTerm(RingFuncTerm, FieldElement, ACTerm):
    def __init__(self, r : Ring, term : ACTerm):
        RingFuncTerm.__init__(self, r, term)
        FieldElement.__init__(self, r)
        ACTerm.__init__(self, term.function, term.arguments)
        self.term = term

class FieldConstant(RingConstant, FieldElement):
    def __init__(self, f : Field, symbol : str):
        RingConstant.__init__(self, f, symbol)
        FieldElement.__init__(self, f)