from symcollab.algebra import *
from .ac import *
from copy import deepcopy

# This is a single arity function which only actually gets applied when called an odd number of times
# Useful for the inverse function later on


# A group G is an algebraic structure which satisfies the following properties
# (1) G is closed under the operation
# (2) The operation is associative
# (3) An identity element exists [that is, op(x, id) = x for all x in G]
# (4) An inverse exists for each element
class Group:
    def __init__(self, name : str, operation : AFunction, inv_symbol = None, identity_symbol = "e"):
        if not isinstance(operation, AFunction):
            raise ValueError("operation must be associative (AFunction)")
        self.name = name
        self.identity = GroupConstant(self, identity_symbol)
        self.inv = GroupInverseFunction(self, name + "_inv" if inv_symbol is None else inv_symbol) 
        self.op = GroupFunction(self, operation)
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, x):
        return type(self) is type(x) and self.name == x.name and self.op == x.op

class GroupInverseFunction(Function):
    def __init__(self, g : Group, symbol : str):
        super().__init__(symbol, 1)
        self.group = g
    def __call__(self, x):
        # The inverse of zero in a group is zero
        if x == self.group.identity:
            return deepcopy(self.group.identity)
        if isinstance(x, FuncTerm) and isinstance(x.function, GroupInverseFunction):
            return x.arguments[0]
        return FuncTerm(self, (x,))

class GroupFunction(Function):
    def __init__(self, g : Group, f : Function):
        super().__init__(f.symbol, f.arity)
        self.group = g
        self.function = f
    def __call__(self, *args):
        term = self.function(*args)
        # Important for function calls that returns only a constant
        if not isinstance(term, FuncTerm) or term.function.arity == 0:
            return deepcopy(term)
        result = GroupFuncTerm(self.group, term)
        result.set_function(self)
        return result

# Class that describes an element of the group.
# FuncTerms, Constants, and Variables all inherit from this group
# Multiplication is defined so that you can multiply elements like a * b
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
        # To get around the problem with Substitute Terms
        if isinstance(x, SubstituteTerm):
            return NotImplemented
        matched, term = self._groupmulprops(x)
        result = self.group.op(self, x) if not matched else term
        return self.group.simplify_term(result) if hasattr(self.group, 'simplify_term') else result
    def __rmul__(self, x):
        matched, term = self._groupmulprops(x)
        result = self.group.op(x, self) if not matched else term
        return self.group.simplify_term(result) if hasattr(self.group, 'simplify_term') else result
    # a / b is defined as a * inv(b)
    def __truediv__(self, x):
        return self.__mul__(self.group.inv(x))
    def __rtruediv__(self, x):
        return self.__rmul__(self.group.inv(x))

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
    def set_arguments(self, args):
        self.term.arguments = tuple(args)
        self.arguments = tuple(args)
    def set_function(self, function : Function):
        self.function = function
        self.term.function = function
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

# An abelian group is a group where the operation is also commutative
class AbelianGroup(Group):
    def __init__(self, name : str, operation : ACFunction, inv_symbol = None, identity_symbol = "e"):
        if not isinstance(operation, ACFunction):
            raise ValueError("operation must be associative and commutative (ACFunction)")
        super().__init__(name, operation, inv_symbol = inv_symbol, identity_symbol = identity_symbol)