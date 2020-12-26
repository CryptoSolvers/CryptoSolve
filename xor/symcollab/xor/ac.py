#!/usr/bin/env python3
from typing import Any, List
from collections import Counter
from symcollab.algebra import Function, FuncTerm, Term

#
## Associative Functions
#

class AFunction(Function):
    def __init__(self, symbol: str, arity: int):
        assert arity > 0
        super().__init__(symbol, arity)
    def __call__(self, *args, simplify=True) -> FuncTerm:
        term = ATerm(self, tuple(args[:self.arity]))
        for i in range(self.arity, len(args), self.arity - 1):
            l = args[i:(i + self.arity - 1)]
            term = ATerm(self, (term, *l))
        return term


def _flatten_sublist(l: List[Any]) -> List[Any]:
    new_list: List[Any] = []
    for li in l:
        if hasattr(li, '__iter__'):
            new_list.extend(li)
        else:
            new_list.append(li)
    return new_list

class ATerm(FuncTerm):
    def __init__(self, function: Function, args):
        super().__init__(function, args)
    def flatten(self) -> List[Term]:
        terms: List[Term] = []
        for t in self.arguments:
            if isinstance(t, ATerm) and t.function == self.function:
                sublist = list(map(lambda t: t.flatten() if isinstance(t, ATerm) else t, t.arguments))
                terms += _flatten_sublist(sublist)
            else:
                terms += [t]
        return terms
    def __eq__(self, x):
        return isinstance(x, ATerm) and self.function == x.function and self.flatten() == x.flatten()
    def __hash__(self):
        return FuncTerm.__hash__(self)


#
## Commutative Functions
#

class CFunction(Function):
    def __init__(self, symbol : str, arity : int):
        super().__init__(symbol, arity)
    def __call__(self, *args) -> FuncTerm:
        return CTerm(self, args)


class CTerm(FuncTerm):
    def __init__(self, function: Function, args):
        super().__init__(function, args)
    def __eq__(self, x):
        return isinstance(x, CTerm) and self.function == x.function and Counter(self.arguments) == Counter(x.arguments)
    def __hash__(self):
        return FuncTerm.__hash__(self)

#
## Associative-Commutative Functions
#

class ACFunction(AFunction, CFunction):
    def __init__(self, symbol: str, arity: int):
        super().__init__(symbol, arity)
    # __call__ violates Liskov Substitution Principle?
    def __call__(self, *args) -> FuncTerm: # type: ignore
        term = ACTerm(self, tuple(args[:self.arity]))
        for i in range(self.arity, len(args), self.arity - 1):
            l = args[i:(i + self.arity - 1)]
            term = ACTerm(self, (term, *l))
        return term


class ACTerm(ATerm, CTerm):
    def __init__(self, function: Function, args):
        super().__init__(function, args)
    def __eq__(self, x):
        return isinstance(x, ACTerm) and self.function == x.function and Counter(self.flatten()) == Counter(x.flatten())
    def __hash__(self):
        return FuncTerm.__hash__(self)

