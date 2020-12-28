"""
Some algorithms from meadows.csf21.v2
These are still in experimental form and need polishing/testing


"""
from typing import Tuple, Dict, List, Optional
from algebra import Term, Function, Variable, Constant, FuncTerm
from xor import xor
from xor.structure import Zero

__all__ = [
    'moo_depth_random_check'
]

f = Function("f", 1)
zero = Zero()


#Def 8.1: quasi-unsafe
def search_for_quasi_unsafe(ciphertext: Term, previous_ciphertexts: List[Term],
                         constraints: Dict[Variable, List[Term]]) -> bool:
    """
    Search through the known ciphertext history and see if they are quasi-unsafe.
    """
    qunsafe = False
    for known_ciphertext in previous_ciphertexts:
        collisions = find_collision(known_ciphertext, ciphertext, constraints, unif_algo)
        if any_unifiers(collisions):
            return collisions
    return collisions
