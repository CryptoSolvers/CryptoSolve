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


