#!/usr/bin/env python3
import typing
from typing import Union, Any, Optional
from copy import deepcopy
from .term import *

class AssocFunction(Function):
    def __init__(self, symbol : str, arity : int):
        assert arity > 0
        super(AssocFunction, self).__init__(symbol, arity)
    def __call__(self, *args, simplify = True):
        term = AssocTerm(self, tuple(args[:self.arity]))
        for i in range(self.arity, len(args), self.arity - 1):
            l = args[i:(i + self.arity - 1)]
            term = AssocTerm(self, (term, *l))
        return term

def _flatten_sublist(l):
    new_list = []
    for li in l:
        if hasattr(li, '__iter__'):
            new_list.extend(li)
        else:
            new_list.append(li)
    return new_list
class AssocTerm(FuncTerm):
    def __init__(self, function : Function, args):
        super(AssocTerm, self).__init__(function, args)
    def flatten(self):
        terms = []
        for t in self.arguments:
            if isinstance(t, AssocTerm) and t.function == self.function:
                sublist = list(map(lambda t: t.flatten() if isinstance(t, AssocTerm) else t, t.arguments))
                terms += _flatten_sublist(sublist)
            else:
                terms += [t]
        return terms