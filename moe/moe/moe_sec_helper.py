"""
Functions that check syntatically
the security of a mode of operation.

Based on Hai Lin's work.
"""
from typing import Tuple
from algebra import Term, Function, Variable, Constant, FuncTerm
from xor import xor

__all__ = [
    'moe_syntactic_condition', 'moe_syn_security',
    'moe_has_random', 'moe_f_depth'
]

f = Function("f", 1)

def moe_syntactic_condition(block: Term, next_block: Term) -> bool:
    """
    Given two sequential cipher texts, analyze whether
    or not the mode of operation is secure.
    """
    # TODO: Find out how to say what the current plaintext is
    next_plaintext = Variable("x_i")

    if xor(block, next_plaintext) in next_block:
        return False

    if f(next_plaintext) in next_block:
        return False

    # TODO: Actually implement
    last_cipher_under_f = lambda block, next_block: True
    if not last_cipher_under_f(block, next_block):
        return False

    # At this point it passed the syntactic conditions
    return True # AKA Maybe


# TODO: We have to somehow take variables into account....
# We would likely do this by constraining what our plaintext could be.
# "Each variable x_i can only be mapped to the xor of some terms
#  in {C_0, C_1, ..., C_{i - 1}}"

def overlaps(low1: int, high1: int, low2: int, high2: int) -> bool:
    """
    Returns true if the two regions
    [low1, high1] and [low2, high2]
    overlaps.
    """
    return high1 >= low2 or low1 >= high2

def moe_f_depth(t: Term) -> Tuple[int, int]:
    """
    Returns the range of the possible number
    of nested f symbols in t under all possible
    substitutions for a ***ground*** term.
    """
    #Check if t is a constant
    if isinstance(t, Constant):
        return 0, 0

    if isinstance(t, FuncTerm):
        if t.function == f:
            low, high = moe_f_depth(t.arguments[0])
            return low + 1, high + 1

        if t.function == xor:
            low1, high1 = moe_f_depth(t.arguments[0])
            low2, high2 = moe_f_depth(t.arguments[1])
            if overlaps(low1, high1, low2, high2):
                return 0, max(high1, high2)
            return max(low1, low2), max(high1, high2)

    raise ValueError("Variable or Function outside valid signature for moe_f_depth.")


def moe_has_random(t: Term) -> bool:
    """
    Returns true if and only if a ground
    term t always contains a constant
    under all possible substitutions
    for variables.
    """
    if isinstance(t, Variable):
        return False

    if isinstance(t, Constant):
        return True

    if isinstance(t, FuncTerm):
        if t.function == f:
            return moe_has_random(t.arguments[0])

        if t.function == xor:
            # Make sure at least one of the arguments
            # has randomness
            if not moe_has_random(t.arguments[0]) and \
                not moe_has_random(t.arguments[1]):
                return False

            low1, high1 = moe_f_depth(t.arguments[0])
            low2, high2 = moe_f_depth(t.arguments[1])
            return not overlaps(low1, high1, low2, high2)

    raise ValueError("Variable or Function outside valid signature for moe_f_depth.")


def moe_syn_security(block, next_block):
    """
    Given two sequential blocks from a
    mode of operation, return whether
    the mode of operation is secure.
    """
    _, high1 = moe_f_depth(block)
    low2, high2 = moe_f_depth(next_block)
    return low2 == high2 and \
           high2 > high1 and \
           moe_has_random(block) and \
           moe_has_random(next_block)
