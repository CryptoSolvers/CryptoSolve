"""
Functions that check syntatically
the security of a mode of operation.

Based on Hai Lin's work.
"""
from typing import Tuple, Dict, List, Optional
from algebra import Term, Function, Variable, Constant, FuncTerm
from xor import xor
from xor.structure import Zero

__all__ = [
    'moe_syntactic_condition', 'moe_syn_security',
    'moe_has_random', 'moe_f_depth'
]

f = Function("f", 1)
zero = Zero()

def last_block_under_f(last_block: Term, block: Term) -> bool:
    """
    Checks to see if the last block is under an f in the current block.
    """
    if isinstance(block, FuncTerm):
        if block.function == f:
            return last_block in block
        # Go through each of the arguments and return true
        # if any are true.
        return any(
            last_block_under_f(last_block, arg) for arg in block.arguments
        )
    return False

def moe_syntactic_condition(last_block: Term, block: Term) -> bool:
    """
    Given two sequential cipher texts, analyze whether
    or not the mode of operation is secure.

    False in this context means a maybe.
    """
    plaintext = Variable("x_i")

    if xor(last_block, plaintext) in block:
        return False

    if f(plaintext) in block:
        return False

    if not last_block_under_f(last_block, block):
        return False

    # At this point it passed the syntactic conditions
    return True

def overlaps(low1: int, high1: int, low2: int, high2: int) -> bool:
    """
    Returns true if the two regions
    [low1, high1] and [low2, high2]
    overlap.
    """
    return high1 >= low2 and high2 >= low1

def moe_f_depth(t: Term, possible_subs: Optional[Dict[Term, List[Term]]] = None) -> Tuple[int, int]:
    """
    Returns the range of the possible number
    of nested f symbols in t under all possible
    substitutions for a term.
    """
    if isinstance(t, Variable):
        if possible_subs is None or t not in possible_subs.keys() or len(possible_subs[t]) == 0:
            raise ValueError(f"Unable to determine possible substitutions for variable {t}.")
        possible_f_depths = [moe_f_depth(ti, possible_subs) for ti in possible_subs[t]]
        lows, highs = zip(*possible_f_depths)
        return min(lows), max(highs)

    if isinstance(t, Constant):
        return 0, 0

    if isinstance(t, FuncTerm):
        if t.function == f:
            low, high = moe_f_depth(t.arguments[0], possible_subs)
            return low + 1, high + 1

        if t.function == xor:
            low1, high1 = moe_f_depth(t.arguments[0], possible_subs)
            low2, high2 = moe_f_depth(t.arguments[1], possible_subs)
            if overlaps(low1, high1, low2, high2):
                return 0, max(high1, high2)
            return max(low1, low2), max(high1, high2)

    raise ValueError("Function outside valid signature for moe_f_depth.")


def moe_has_random(t: Term, possible_subs: Optional[Dict[Term, List[Term]]] = None) -> bool:
    """
    Returns true if and only if a
    term t always contains a constant
    under all possible substitutions
    for variables.
    """
    if isinstance(t, Variable):
        if possible_subs is None or t not in possible_subs.keys() or len(possible_subs[t]) == 0:
            raise ValueError(f"Unable to determine possible substitutions for variable {t}.")
        return all(moe_has_random(arg, possible_subs) for arg in possible_subs[t])

    if t == zero:
        return False

    if isinstance(t, Constant):
        return True

    if isinstance(t, FuncTerm):
        if t.function == f:
            return moe_has_random(t.arguments[0], possible_subs)

        if t.function == xor:
            # Make sure at least one of the arguments
            # has randomness
            if not moe_has_random(t.arguments[0], possible_subs) and \
                not moe_has_random(t.arguments[1], possible_subs):
                return False

            low1, high1 = moe_f_depth(t.arguments[0], possible_subs)
            low2, high2 = moe_f_depth(t.arguments[1], possible_subs)
            return not overlaps(low1, high1, low2, high2)

    raise ValueError("Function outside valid signature for moe_f_depth.")


def moe_syn_security(block: Term, next_block: Term, possible_subs: Optional[Dict[Term, List[Term]]] = None) -> bool:
    """
    Given two sequential blocks from a
    mode of operation, return whether
    the mode of operation is secure.
    """
    _, high1 = moe_f_depth(block, possible_subs)
    low2, high2 = moe_f_depth(next_block, possible_subs)
    return low2 == high2 and \
           high2 > high1 and \
           moe_has_random(block, possible_subs) and \
           moe_has_random(next_block, possible_subs)
