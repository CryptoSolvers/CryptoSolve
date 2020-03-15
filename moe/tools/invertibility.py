from algebra import *
from copy import deepcopy
from xor import xor
from collections import Counter

def invert_simple(term):
    """
    Algorithm to get the plaintext P_{i} out of a MOE.
    
    Works by moving up in the DAG from the plaintext variable
    Applying the reverse transformation as it moves along
    f -> f^{-1}
    xor(P, x) -> xor(P, xor(x, x)) -> P

    Assumptions:
      - Previous plaintexts aren't in the term
      - The plaintext is only in one position
    """
    P = Variable("P_{i}")
    f = Function("f", 1)
    finv = Function("f^{-1}", 1)

    inverseTerm = Variable("x")
    transforms = []

    d = TermDAG(term)
    # Check second assumption
    assert Counter(d.leaves())[P] == 1

    currentTerm = deepcopy(P)
    parentTerm = list(d.parents(currentTerm))
    while parentTerm != []:
        # Second assumption check
        assert len(parentTerm) == 1
        parentTerm = parentTerm[0]
        if parentTerm.function == f:
            transforms.append((finv,))
        elif parentTerm.function == xor:
            # Cancel out the xor by xoring with
            # the other argument again.
            if parentTerm.arguments[0] == currentTerm:
                transforms.append((xor, parentTerm.arguments[1]))
            else:
                transforms.append((xor, parentTerm.arguments[0]))
        else:
            raise ValueError("A function other than f or xor detected")
        currentTerm = deepcopy(parentTerm)
        parentTerm = list(d.parents(parentTerm))
    
    for transform in reversed(transforms):
        if transform[0] == finv:
            inverseTerm = finv(inverseTerm)
        else: # Assume xor
            inverseTerm = xor(inverseTerm, transform[1])
    
    return inverseTerm


def moe_invert(K : Set[Term], nounces : Set[Constant], S : int) -> bool:
    """
    IN PROGRESS
    Given a set K of MOE interactions and max bound for the depth of a term,
    state whether or not a MOE term is invertible.
    """
    P = Constant("P")
    f = Function("f", 1)
    if P not in K:
        return False
    # Compute K*
    K_star = K | nounces
    # From K* construct C*
    C_star = deepcopy(K_star)
    current_length = 0
    while len(C_star) != current_length:
        current_length = len(C_star)
        for t_1 in C_star:
            # Definition 15 (2a)
            if isinstance(t_1, FuncTerm) and t.function == f:
                # Apply f inverse
                C_star |= t_1.arguments[0]
            # Definition 15 (2b)
            for t_2 in C_star:
                new_term_b = xor(t_1, t_2)
                if depth(new_term_b) <= S:
                    C_star |= new_term_b
            # Definition 15 (2c)
            new_term_c = f(t_1)
            if depth(new_term_c) <= S:
                C_star |= new_term_c
    # Next goes the checking logic....

