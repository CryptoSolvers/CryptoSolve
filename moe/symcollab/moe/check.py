"""
Module to check security of modes of operations.
"""
from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Union
from symcollab.algebra import SubstituteTerm, Term, Variable
from symcollab.Unification.p_unif import p_unif
from symcollab.xor.structure import Zero
from .program import MOOProgram
from .collisions import find_collision
from .syntactic_check import moo_depth_random_check
from .invertibility import InvertMOO


__all__ = ['moo_check']

def moo_check(moo_name: str = 'cipher_block_chaining', schedule_name: str = 'every',
              unif_algo: Callable = p_unif, length_bound: int = 10,
              knows_iv: bool = True, invert_check: bool = False) -> 'MOOCheckResult':
    """
    Simulates a MOOProgram interaction and checks if any conditions for security fails.
    Currently it checks syntactically and for collisions.

    Parameters
    ==========
    moo_name: str
      Name of the mode of operation to consider.
    schedule_name: str
      Name of the schedule to consider.
    unif_algo: Callable
      Unification algorithm to use when checking for collisions
    length_bound: int
      The maximum interactions to check for collisions. Default is 10.
    knows_iv: bool
      Whether or not the adversary knows the initialization vector.

    """
    program = MOOProgram(moo_name, schedule_name)
    xor_zero = Zero()
    constraints: Dict[Variable, List[Term]] = dict()
    known_terms: List[Term] = [xor_zero, program.nonces[0]] if knows_iv else [xor_zero]
    ciphertexts_received: List[Term] = list()
    result = None
    invertible = False
    # Start interactions
    
    for i in range(1, length_bound + 1):
        plaintext = Variable(f"x_{i}")
        constraints[plaintext] = deepcopy(known_terms)
        known_terms.append(plaintext)

        result = program.rcv_block(plaintext)
        if result is not None:
            ciphertext = unravel(result.message, result.substitutions)
            
            #check for invertibility
            if invert_check and i == 1:
                invertible = InvertMOO(ciphertext, f"x_{i}", knows_iv)

            # Check for syntactic security
            if len(ciphertexts_received) > 1:
                last_ciphertext = ciphertexts_received[-1]
                if moo_depth_random_check(last_ciphertext, ciphertext, constraints):
                    return MOOCheckResult(True, None, invertible)

            # Check for collisions
            collisions = search_for_collision(
                ciphertext,
                ciphertexts_received,
                constraints,
                unif_algo
            )
            if any_unifiers(collisions):
                return MOOCheckResult(False, collisions, invertible)

            known_terms.append(ciphertext)
            ciphertexts_received.append(ciphertext)


    # Stop Interaction
    last_result = program.rcv_stop()

    # If the last block wasn't returned, we'll use the stop frame to check
    if result is None:
        ciphertext = unravel(last_result.message, last_result.substitutions)
        collisions = search_for_collision(ciphertext, ciphertexts_received, constraints, unif_algo)
        if any_unifiers(collisions):
            return MOOCheckResult(False, collisions, invertible)

    # If we got this far then no unifiers were found
    print("No unifiers found.")
    return MOOCheckResult(False, None, invertible)


def search_for_collision(ciphertext: Term, previous_ciphertexts: List[Term],
                         constraints: Dict[Variable, List[Term]],
                         unif_algo: Callable) -> Optional[Union[SubstituteTerm, List[SubstituteTerm]]]:
    """
    Search through the known ciphertext history and see if there are any collisions
    between the current ciphertext and a past one.
    """
    collisions = None
    for known_ciphertext in previous_ciphertexts:
        collisions = find_collision(known_ciphertext, ciphertext, constraints, unif_algo)
        if any_unifiers(collisions):
            return collisions
    return collisions

def unravel(t: Term, s: SubstituteTerm) -> Term:
    """Apply a substitution until you can't"""
    while t != t * s:
        t = t * s
    return t

def any_unifiers(unifiers: Optional[Union[bool, SubstituteTerm, List[SubstituteTerm]]]) -> bool:
    """Searches a list of unifiers to see if any of them have an entry"""
    if not unifiers:
        return False
    if isinstance(unifiers, SubstituteTerm):
        if len(unifiers) > 0:
            return True
    if unifiers is not None:
        return any(
            (len(u) > 0 for u in unifiers)
        )
    return False


@dataclass
class MOOCheckResult:
    """
    Result of the moo_check function.

    Parameters
    ==========
    syntactic_result
      Whether or not it passes the syntactic conditions.
    collisions
      Result of the unification algorithm attempting to find a
      substitution that causes two ciphertexts to collapse to zero.
    """
    syntactic_result: bool
    collisions: Optional[Union[bool, SubstituteTerm, List[SubstituteTerm]]]
    invert_result: bool

    @property
    def secure(self) -> bool:
        """
        State whether the MOOCheckResult implies
        secureness or not.
        """
        return self.syntactic_result or not any_unifiers(self.collisions)
