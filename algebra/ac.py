#!/usr/bin/env python3
import typing
from typing import Union, Any, Optional
from copy import deepcopy
from .term import *
from collections import Counter

#
## Associative Functions
#

class aFunction(Function):
    def __init__(self, symbol : str, arity : int):
        assert arity > 0
        super(aFunction, self).__init__(symbol, arity)
    def __call__(self, *args, simplify = True):
        term = aTerm(self, tuple(args[:self.arity]))
        for i in range(self.arity, len(args), self.arity - 1):
            l = args[i:(i + self.arity - 1)]
            term = aTerm(self, (term, *l))
        return term
    def __eq__(self, x):
        return isinstance(x, aFunction) and self.symbol == x.symbol

def _flatten_sublist(l):
    new_list = []
    for li in l:
        if hasattr(li, '__iter__'):
            new_list.extend(li)
        else:
            new_list.append(li)
    return new_list

class aTerm(FuncTerm):
    def __init__(self, function : Function, args):
        super(aTerm, self).__init__(function, args)
    def flatten(self):
        terms = []
        for t in self.arguments:
            if isinstance(t, aTerm) and t.function == self.function:
                sublist = list(map(lambda t: t.flatten() if isinstance(t, aTerm) else t, t.arguments))
                terms += _flatten_sublist(sublist)
            else:
                terms += [t]
        return terms
    def __eq__(self, x):
        return isinstance(x, aTerm) and self.function == x.function and self.flatten() == x.flatten()


#
## Commutative Functions
#

class cFunction(Function):
    def __init__(self, symbol : str, arity : int):
        super(cFunction, self).__init__(symbol, arity)
    def __call__(self, *args):
        return cTerm(self, args)
    def __eq__(self, x):
        return isinstance(x, cFunction) and self.symbol == x.symbol


class cTerm(FuncTerm):
    def __init__(self, function : Function, args):
        super(cTerm, self).__init__(function, args)
    def __eq__(self, x):
        return isinstance(x, cTerm) and self.function == x.function and Counter(self.arguments) == Counter(x.arguments)

#
## Associative-Commutative Functions
#

class acFunction(aFunction, cFunction):
    def __init__(self, symbol : str, arity : int):
        super(acFunction, self).__init__(symbol, arity)
    def __call__(self, *args):
        term = acTerm(self, tuple(args[:self.arity]))
        for i in range(self.arity, len(args), self.arity - 1):
            l = args[i:(i + self.arity - 1)]
            term = acTerm(self, (term, *l))
        return term
    def __eq__(self, x):
        return isinstance(x, acFunction) and self.symbol == x.symbol


class acTerm(aTerm, cTerm):
    def __init__(self, function : Function, args):
        super(acTerm, self).__init__(function, args)
    def __eq__(self, x):
        return isinstance(x, acTerm) and self.function == x.function and Counter(self.flatten()) == Counter(x.flatten())