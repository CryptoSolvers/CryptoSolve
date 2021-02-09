"""
Some algorithms from meadows.csf21.v2
These are still in experimental form and need polishing/testing


"""
from typing import Tuple, Dict, List, Optional
from algebra import Term, Function, Variable, Constant, FuncTerm
from xor import xor
from xor.structure import Zero


f = Function("f", 1)
zero = Zero()


#Def 6.4: degenerate

def degenerate_check(ciphertext: Term, previous_ciphertexts: List[Term]) -> bool:
    """
    Check if symbolic history is degenerate
    """
    degen = False
    previous_ciphertexts.append(ciphertext)
    seq = zero
    for t in previous_ciphertexts:
        seq = xor(seq, t)
        if seq == zero:
            degen = True
            break
    return degen

#Def 8.1: quasi-unsafe
def search_for_quasi_unsafe(ciphertext: Term, constraints: Dict[Variable, List[Term]]) -> bool:
    """
    Search through the known ciphertext history and see if they are quasi-unsafe.
    """
    qunsafe = False
    #check if current term is f-rooted
    if isinstance(ciphertext, FuncTerm) and ciphertext.function == f:
        if isinstance(ciphertext.arguments[0], FuncTerm) and ciphertext.arguments[0].function == xor:
            args = ciphertext.arguments[0].arguments
            for z in args:
                if isinstance(z, Variable):
                    if z in constraints.keys():
                        argset = set(args)
                        dset = set(constraints[z])
                        if len(argset.intersection(dset)) > 0:
                            qunsafe = True 
    return qunsafe
