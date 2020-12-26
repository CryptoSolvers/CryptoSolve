"""
Functions that check syntatically
the security of a mode of operation.

Based on Hai Lin's work.
"""
from typing import Tuple, Dict, List, Optional
from symcollab.algebra import Term, Function, Variable, Constant, FuncTerm
from symcollab.xor import xor
from symcollab.xor.structure import Zero

__all__ = [
    'moo_depth_random_check'
]

f = Function("f", 1)
zero = Zero()

def moo_depth_random_check(last_block: Term, block: Term,
                           possible_subs: Optional[Dict[Term, List[Term]]] = None) -> bool:
    """
    Given two sequential ciphertexts, infer whether the
    mode of operation is secure by analyzing the depths
    of encryption applied and whether it has randomness.

    False in this context means a maybe.
    """
    _, last_high = moo_f_depth(last_block, possible_subs)
    low, high = moo_f_depth(block, possible_subs)
    return low == high and \
           high > last_high and \
           moo_has_random(last_block, possible_subs) and \
           moo_has_random(block, possible_subs)

def overlaps(low1: int, high1: int, low2: int, high2: int) -> bool:
    """
    Returns true if the two regions
    [low1, high1] and [low2, high2]
    overlap.
    """
    return high1 >= low2 and high2 >= low1


def moo_f_depth(t: Term, possible_subs: Optional[Dict[Term, List[Term]]] = None) -> Tuple[int, int]:
    """
    Returns the range of the possible number
    of nested f symbols in t under all possible
    substitutions for a term.
    """
    if isinstance(t, Variable):
        if possible_subs is None or t not in possible_subs.keys() or len(possible_subs[t]) == 0:
            raise ValueError(f"Unable to determine possible substitutions for variable {t}.")
        possible_f_depths = [moo_f_depth(ti, possible_subs) for ti in possible_subs[t]]
        lows, highs = zip(*possible_f_depths)
        return min(lows), max(highs)

    if isinstance(t, Constant):
        return 0, 0

    if isinstance(t, FuncTerm):
        if t.function == f:
            low, high = moo_f_depth(t.arguments[0], possible_subs)
            return low + 1, high + 1

        if t.function == xor:
            low1, high1 = moo_f_depth(t.arguments[0], possible_subs)
            low2, high2 = moo_f_depth(t.arguments[1], possible_subs)
            if overlaps(low1, high1, low2, high2):
                return 0, max(high1, high2)
            return max(low1, low2), max(high1, high2)

    raise ValueError("Function outside valid signature for moo_f_depth.")


def moo_has_random(t: Term, possible_subs: Optional[Dict[Term, List[Term]]] = None) -> bool:
    """
    Returns true if and only if a
    term t always contains a constant
    under all possible substitutions
    for variables.
    """
    if isinstance(t, Variable):
        if possible_subs is None or t not in possible_subs.keys() or len(possible_subs[t]) == 0:
            raise ValueError(f"Unable to determine possible substitutions for variable {t}.")
        return all(moo_has_random(arg, possible_subs) for arg in possible_subs[t])

    if t == zero:
        return False

    if isinstance(t, Constant):
        return True

    if isinstance(t, FuncTerm):
        if t.function == f:
            return moo_has_random(t.arguments[0], possible_subs)

        if t.function == xor:
            # Make sure at least one of the arguments
            # has randomness
            if not moo_has_random(t.arguments[0], possible_subs) and \
                not moo_has_random(t.arguments[1], possible_subs):
                return False

            low1, high1 = moo_f_depth(t.arguments[0], possible_subs)
            low2, high2 = moo_f_depth(t.arguments[1], possible_subs)
            return not overlaps(low1, high1, low2, high2)

    raise ValueError("Function outside valid signature for moo_f_depth.")
