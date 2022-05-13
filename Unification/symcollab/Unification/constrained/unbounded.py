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
        super().__init__(self.symbol)
        
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
        new_arguments = list()
        for arg in t.arguments:
            new_arguments.append(to_constant_term_bound(arg, i))
        return xor(*new_arguments)
    if (isinstance(t, FuncTerm) and t.function.symbol != "xor"):
        new_arguments = list()
        for arg in t.arguments:
            new_arguments.append(to_constant_term_bound(arg, i))
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
        if self.omega_superscript == float('inf'):
            return f"omega * " + super().__str__()
        else:
            return f"omega^j-{self.omega_superscript} * " + super().__str__()

    def _applysub(self, term: Term) -> Term:
        if self.omega_superscript == float('inf'):
            return super()._applysub(term)
        else:
            new_term = to_constant_term_bound(term, self.omega_superscript)
            t = super()._applysub(new_term)
            print(t)
            return t

    def __mul__(self, theta):
        subst = super().__mul__(theta)
        omega_substitution = OmegaSubstituteTerm(self.omega_superscript)
        omega_substitution.subs = subst
        return omega_substitution

class Unification_state():

    def __init__(self, equations, substitution):
        self.equations = equations
        self.substitution = substitution

    def is_empty(self):
        return self.equations == []

    def get_result(self):
        return self.substitution

    def print(self):
        print(self.equations)
        print(self.substitution)

def split_Y(state):
    eqs = state.equations
    subst = state.substitution

    first = eqs[0]
    remaining_eqs = eqs[1:]

    lhs = first.left_side
    rhs = first.right_side
    lhs_summands = summands(lhs)
    rhs_summands = summands(rhs)
    applicable = containsY(lhs_summands)

    if(applicable):
        (Y_term1, others1) = split_terms_Y(lhs_summands)
        (Y_term2, others2) = split_terms_wrt_term_Y(rhs_summands, Y_term1)

        eq1 = Equation(Y_term1, Y_term2)
        if(len(others1) == 1):
            eq2 = Equation(*others1, *others2)
        else:
            eq2 = Equation(xor(*others1), xor(*others2))
        

        remaining_eqs.append(eq1)
        remaining_eqs.append(eq2)

        return (applicable, Unification_state(remaining_eqs, subst))
    else:
        return (applicable, state)

def apply_rules(state):
    #This part is similar to the bounded case except that we have some more rules:
    #Cancel_Y and Split_Y
    while(not state.is_empty()):
        (successful, new_state) = decompose(state)
        if(successful):
            print("decompose rule applied.")
            state = new_state
            print("new state:")
            state.print()
            continue

        (successful, new_state) = elim_c(state)
        if(successful):
            print("elim_c rule applied.")
            state = new_state
            print("new state:")
            state.print()
            continue

        (successful, new_state) = elim_tk(state)
        if(successful):
            print("elim_tk rule applied.")
            state = new_state
            print("new state:")
            state.print()
            continue

        (successful, new_state) = split(state)
        if(successful):
            print("split rule applied.")
            state = new_state
            print("new state:")
            state.print()
            continue

        (successful, new_state) = split_Y(state)
        if(successful):
            print("split_Y rule applied.")
            state = new_state
            print("new state:")
            state.print()
            continue

        (successful, new_state) = Cancel_Y(state)
        if(successful):
            print("Cancel_Y rule applied.")
            state = new_state
            print("new state:")
            state.print()
            continue

    return state.get_result()


def test1():
    Y = YVariable(0)
    T = TVariable(0)
    e = Function('e', 2)
    n = NFunction(1)
    C1 = CVariable(1)
    D = Variable('D')
    c = Constant('c')
    t = e(n(T), C1)
    print(t)

    sigma1 = OmegaSubstituteTerm()
    sigma2 = SubstituteTerm()
    sigma2.add(C1, c)
    print(sigma1 * sigma2)
    




test1()

