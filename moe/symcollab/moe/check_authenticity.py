"""
Module to check security of modes of operations.
"""
from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Union
from symcollab.algebra import SubstituteTerm, Term, Variable, Constant, Function
from symcollab.Unification.constrained.p_unif import p_unif
from symcollab.xor.structure import Zero
from .program import MOOProgram
from .collisions import find_collision
from .syntactic_check import moo_depth_random_check
from .invertibility import InvertMOO
from symcollab.Unification.constrained.xor_rooted_unif import XOR_rooted_security
from symcollab.Unification.constrained.authenticity import *
from .symbolic_check import symbolic_check
from symcollab.Unification.constrained import *

__all__ = ['check_authenticity']

e = Function("e", 2)
d = Function("d", 2)
n = Function("n", 1)
C1 = IndexedVariable("C1")
C2 = IndexedVariable("C2")
T = IndexedVariable("T")

bounded_dict = {'AE-Scheme1': e(n(n(T)), d(n(T), xor(d(T, C1), C2))), 'AE-Scheme2': e(n(n(T)), d(T, xor(d(n(T), C2), C1))), 'AE-Scheme3': e(n(n(T)), xor(d(T, C1), d(n(T), C2))), 'AE-Scheme4': e(n(n(T)), xor(C1, d(n(T), C2))),'AE-Scheme5': e(n(n(T)), xor(C1, C2))}


def check_authenticity(ae_name):
    check_security(bounded_dict[ae_name])
    
