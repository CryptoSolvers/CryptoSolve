"""
Module to support the MOO_Tool in
finding collisions.
"""
from typing import Callable, Dict, List, Optional
from symcollab.algebra import Equation, SubstituteTerm, Term, Variable
from symcollab.Unification.p_unif import p_unif
from symcollab.Unification.p_syntactic import p_syntactic
from symcollab.Unification.xor_rooted_unif import XOR_rooted_security
from symcollab.xor.structure import Equations

__all__ = ['find_collision']

def find_collision(cipher_text1: Term, cipher_text2: Term,
                   constraints: Dict[Variable, List[Term]],
                   unif_algo: Callable = p_unif) -> Optional[SubstituteTerm]:
    """
    Sets up a unification problem between two ciphertexts in order to see
    if there is a possible collision given some constraints.
    """
    if unif_algo == p_unif:
        unifiers = unif_algo(
            Equations([Equation(cipher_text1, cipher_text2)]),
            constraints
        )
    elif unif_algo == XOR_rooted_security:
        unifiers = unif_algo(
            [cipher_text1, cipher_text2],
            constraints
        ).solve()
    elif unif_algo == p_syntactic:
        unifiers = unif_algo(
            cipher_text1,
            cipher_text2,
            constraints
        )
    else:
        raise ValueError("Unification algorithm provided is not supported.")

    return unifiers
