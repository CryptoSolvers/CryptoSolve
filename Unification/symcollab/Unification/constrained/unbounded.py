from symcollab.algebra import *
from symcollab.algebra.dag import TermDAG
from typing import Optional, Union, Any, List
from symcollab.xor.xor import *
from copy import deepcopy


class TVariable(Variable):
    def __init__(self, sort: Optional[Sort] = None):
        self.symbol = 'T'
        self.sort = sort

    def __repr__(self):
        return 'T'

    def to_constant(self):
        return Constant('t')

class CVariable(Variable):
    def __init__(self, offset, sort: Optional[Sort] = None):
        assert offset >= 0
        if offset == 0:
            self.symbol = 'C'
        else:
            self.symbol = 'C' + f"_j-{offset}"
        self.offset = offset
        self.sort = sort
        
    def to_constant(self):
        return Constant('c' + f"_j-{self.offset}")

class YVariable(Variable):
    def __init__(self, offset, sort: Optional[Sort] = None):
        assert offset >= 0
        if offset == 0:
            self.symbol = 'Y'
        else:
            self.symbol = 'Y' + f"_j-{offset}"
        self.offset = offset
        self.sort = sort
        

class NFunction(Function):
    def __init__(self, offset: int,
                 domain_sort: Union[Optional[Sort], List[Optional[Sort]]] = None,
                 range_sort: Optional[Sort] = None):
        if offset == 0:
            self.symbol = 'n'
        else:
            self.symbol = 'n' + f"^j-{offset}"
        self.domain_sort = domain_sort
        self.range_sort = range_sort
        self.arity = 1
        self.offset = offset

        # If the domain sort is a list, make sure it has a one-to-one mapping with the arguments
        if isinstance(domain_sort, list):
            assert len(domain_sort) == arity

def to_constant_term_bound(t, i):
    # i is a lower bound
    if (isinstance(t, TVariable)):
        return t.to_constant()
    if (isinstance(t, CVariable)):
        if t.offset >= i:
            return t.to_constant()
        else:
            return t
    if (isinstance(t, Constant) or isinstance(t, Variable)):
        return t
    if (isinstance(t, FuncTerm) and t.function.symbol == "xor"):
        new_arguments = list(map(to_constant_term, t.arguments))
        return xor(*new_arguments)
    if (isinstance(t, FuncTerm) and t.function.symbol != "xor"):
        new_arguments = list(map(to_constant_term, t.arguments))
        return FuncTerm(t.function, new_arguments)
    else:
        print("error in to_constant")
        return None

def to_constant_term(t):
    return to_constant_term_bound(t, 0)

class OmegaSubstituteTerm(SubstituteTerm):
    def __init__(self, superscript=float('inf')):
        self.omega_superscript = superscript
        super().__init__()

    def __str__(self):
        return f"omega^{self.omega_superscript} * " + super().__str__()

    def _applysub(self, term: Term) -> Term:
        if self.omega_superscript == float('inf'):
            return super()._applysub(term)
        else:
            new_term = to_constant_term_bound(term, self.omega_superscript)
            return super()._applysub(new_term)

    def __mul__(self, theta):
        subst = super().__mul__(theta)
        omega_substitution = OmegaSubstituteTerm(self.omega_superscript)
        omega_substitution.subs = omega_substitution.subs
        return omega_substitution


def test1():
    Y = YVariable(0)
    T = TVariable(0)
    e = Function('e', 2)
    n = NFunction(1)
    C1 = CVariable(1)
    c = Constant('c')
    t = e(n(T), C1)
    print(t)

    sigma = OmegaSubstituteTerm()
    sigma.add(C1, c)
    print(sigma)
    print(t * sigma)




test1()

