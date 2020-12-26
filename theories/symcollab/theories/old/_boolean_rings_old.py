from symcollab.algebra import *
from .ac import *
from .rings import *
from copy import deepcopy

BooleanRing = Ring("BooleanRing", ACFunction("bool_add", 2), ACIFunction("bool_mul", 2), "0")

def simplify_boolean_term(term : Term) -> Term:
    # A simplification can only occur if we're working with a RingFuncTerm
    if not isinstance(term, RingFuncTerm) or term.ring != BooleanRing:
        return deepcopy(term)
    
    # Flatten args and simplify recursively
    args = term.flatten()
    new_args = []
    for arg in args:
        new_args.append(simplify_boolean_term(arg))
    
    # Apply x + x -> 0
    if term.function == BooleanRing.add:
        var_constant_counts = Counter(new_args)
        new_args = []
        for t, count in var_constant_counts.items():
            # x + x -> 0 implies that we only care about an odd number of x's
            if count % 2 == 1:
                new_args += [t]
    
    # Check length of arguments list and return accordingly
    if len(new_args) > 1:
        term = term.function(*new_args)
    elif len(new_args) == 1:
        term = new_args[0]
    else:
        term = deepcopy(BooleanRing.zero)
    return term

BooleanRing.simplify_term = simplify_boolean_term
