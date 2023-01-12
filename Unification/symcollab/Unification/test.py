from itertools import product
from sympy.solvers.diophantine.diophantine import diop_linear
from sympy import symbols

import functools


def infinite_sequences(vector_len):
    """
    Generate positive instantiations of a vector of a specfied length.

    Ex: infinite_sequences(3)
    [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0]. [1, 0, 1], [1, 1, 0], [1, 1, 1], ...
    """
    first_elem = [0 for _ in range(vector_len)]
    yield first_elem
    result = [first_elem]

    # All the possible ways to increment a vector
    # Skip first one since it's [0, 0, 0]
    incr_vectors = list(product(*(range(2) for _ in range(vector_len))))[1:]
    
    last_result = result

    while True:
        next_result = []
        for last_inst, incr_vector in product(last_result, incr_vectors):
            # Sum both vectors
            possible_vector = list(map(sum, zip(last_inst, incr_vector)))
                
            if possible_vector not in result:
                yield possible_vector
                next_result.append(possible_vector)
        
        result.extend(next_result)
        last_result = next_result


a, b, c, d, e, f, g = symbols("a b c d e f g", integer=True, positive=True)
basis_vector = diop_linear(2 * a + b + c - d - e - f - g)
free_symbols = list(functools.reduce(lambda c, n: c.union(n), (x.free_symbols for x in basis_vector)))
possible_instantiations = infinite_sequences(len(free_symbols))