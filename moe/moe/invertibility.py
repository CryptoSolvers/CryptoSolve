"""
Collection of functions to check if a mode
of operation is invertible.
"""
from collections import Counter
from copy import deepcopy
from typing import Set
from algebra import Constant, depth, Function, FuncTerm, Term, TermDAG, Variable
from xor import xor

__all__ = ['invert_simple', 'moo_invert']

def invert_simple(term):
    """
    Algorithm to get the plaintext P_{i} out of a MOO.

    Works by moving up in the DAG from the plaintext variable
    Applying the reverse transformation as it moves along
    f -> f^{-1}
    xor(P, x) -> xor(P, xor(x, x)) -> P

    Assumptions:
      - Previous plaintexts aren't in the term
      - The plaintext is only in one position
    """
    inverse_term = Variable("x")
    transforms = []

    # Create a TermDAG and check to see
    # that the plaintext is only in one position.
    d = TermDAG(term)
    assert Counter(d.leaves())[_P] == 1

    # Move up the DAG starting from the plaintext
    # leaf and add inverse operations to the
    # transforms list.
    current_term = deepcopy(_P)
    parent_term = list(d.parents(current_term))
    while parent_term != []:
        parent_term = parent_term[0]

        if parent_term.function == _f:
            transforms.append((_finv,))

        elif parent_term.function == xor:
            # Cancel out the xor by xoring with
            # the other argument again.
            if parent_term.arguments[0] == current_term:
                transforms.append((xor, parent_term.arguments[1]))
            else:
                transforms.append((xor, parent_term.arguments[0]))

        else:
            raise ValueError("A function other than f or xor detected")

        current_term = deepcopy(parent_term)
        parent_term = list(d.parents(parent_term))

    # Construct inverse term
    for transform in reversed(transforms):
        if transform[0] == _finv:
            inverse_term = _finv(inverse_term)
        else: # Assume xor
            inverse_term = xor(inverse_term, transform[1])

    return inverse_term


def moo_invert(K: Set[Term], nonces: Set[Constant], S: int) -> bool:
    """
    IN PROGRESS
    Given a set K of MOO interactions and max bound for the depth of a term,
    state whether or not a MOO term is invertible.
    """
    if _P not in K:
        return False
    # Compute K*
    k_star = K | nonces
    # From K* construct C*
    c_star = deepcopy(k_star)
    current_length = 0
    while len(c_star) != current_length:
        current_length = len(c_star)
        for t_1 in c_star:
            # Definition 15 (2a)
            if isinstance(t_1, FuncTerm) and t_1.function == _f:
                # Apply f inverse
                c_star |= t_1.arguments[0]
            # Definition 15 (2b)
            for t_2 in c_star:
                new_term_b = xor(t_1, t_2)
                if depth(new_term_b) <= S:
                    c_star |= new_term_b
            # Definition 15 (2c)
            new_term_c = _f(t_1)
            if depth(new_term_c) <= S:
                c_star |= new_term_c
    # Check to see if the plaintext block is in any of the ground terms in c_star
    # xor library automatically maps terms to their ground terms
    return _P in c_star

_P = Variable("P_{i}")
_f = Function("f", 1)
_finv = Function("f^{-1}", 1)
