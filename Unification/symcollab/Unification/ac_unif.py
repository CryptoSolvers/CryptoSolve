#!/usr/bin/env python3
"""
#Elementary ACU-unification for single term pair

####################################################
To-Do:
-- Add ACU, ACUI, and AG  unification
-- Fix the conversion from the diophantine solver
-- Add free function symbols
-- Allow more than one AC symbol
-- Test the solver and AC solutions
-- Fix variable generation in algorithm
"""
from collections import Counter
from itertools import product
from typing import Set, Dict

import functools

from sympy.solvers.diophantine.diophantine import diop_linear
from sympy.core.sorting import default_sort_key
from sympy import symbols
import sympy

from symcollab.algebra import Equation, get_vars, Variable, SubstituteTerm, Constant, Term, Function
from symcollab.Unification.common import (
    delete_trivial, occurs_check, function_clash
)
from symcollab.Unification.registry import Unification_Algorithms


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


def convert_eq(U: Set[Equation], ac_symbol: Function):
    """
    Convert a set of term equations into a single
    linear homogeneous diophantine equation
    and solve it using Z3.
    """
    var_count = Counter()
    first = True
    # Go through each equation
    for e in U:
        LS = get_vars(e.left_side)
        RS = get_vars(e.right_side)
        VARS_IN_EQ = set(LS).union(set(RS))
        # Go through all the variables in the equation
        for x in VARS_IN_EQ:
            # Update the variable count based on the
            # presense of the variable in the left and right side.
            num = LS.count(x) - RS.count(x)
            var_count[x] += num

    # Create the equation with variable coeficients
    # being the counts above
    sympy_expression = 0
    var_map: Dict[sympy.core.Symbol, Variable] = dict()
    for x, count in var_count.items():
        # Construct Z3 variable
        sympy_var = symbols(x.symbol + "_0", integer=True, positive=True)
        var_map[sympy_var] = x

        # Construct part of expression
        sympy_expression += count * sympy_var


    # Determine the ordering of the diophantine solver output
    sympy_ordering = list(sympy_expression.expand(force=True).free_symbols)
    sympy_ordering.sort(key=default_sort_key)

    # Solve diophantine equation
    basis_vector = diop_linear(sympy_expression)

    ####### Generate table until each column is at least a 1
    # Grab unique free symbols
    free_symbols = list(functools.reduce(lambda c, n: c.union(n), (x.free_symbols for x in basis_vector)))
    possible_instantiations = infinite_sequences(len(free_symbols))
    next(possible_instantiations) # Throw away all zero instantation

    basis_table = []
    finish_generating = False
    while not finish_generating:
        # Instantiate free variables until a valid vector is found
        # Valid is defined as every entry being non-negative with respect to the basis vector.
        valid = False
        while not valid:
            vector = []
            inst = next(possible_instantiations)
            for entry in basis_vector:
                for var_name, count in zip(free_symbols, inst):
                    entry = entry.subs(var_name, count)
                vector.append(int(entry)) # TODO: Can throw an exception?
            # Check validity
            valid = all((entry >= 0 for entry in vector))

        # Add row to the table
        basis_table.append(vector)

        # Check to see if table is finished
        # A table is finished if the sum of every column is greater than 0
        finish_generating = all(sum(col) > 0 for col in zip(*basis_table))

    sigma = SubstituteTerm()
    for column, sympy_var in enumerate(sympy_ordering):
        term = None
        for i, row in enumerate(basis_table):
            row_var = Variable("z_" + str(i)) # TODO: Make sure z_ isnt taken...
            if row[column] > 0:
                # print(f"Add {row[column]} instances of {row_var} to {variables[column]}")
                for _ in range(row[column]):
                    if term is None:
                        term = row_var
                    else: # z_2 + z_4
                        term = ac_symbol(term, row_var)
        sigma.add(var_map[sympy_var], term)

    # Currently returning one posisble unifier but we can keep generating
    # using the basis vector
    return {sigma}

def get_functions(t: Term) -> Set[Function]:
    """Return all function signatures found in a term once each"""
    if isinstance(t, (Constant, Variable)):
        return set()
    
    signatures = {t.function}
    for ti in t.arguments:
        signatures = signatures.union(get_functions(ti))
    
    return signatures


#Assumes currently that we have a single AC-symbol
#need to update to allow other function symbols and cons
@Unification_Algorithms.register('AC')
def ac_unify(U: Set[Equation]):

    # Return no unifiers for a set of empty equations
    if len(U) == 0:
        return False # TODO: return set()

    sigs = set()
    for u in U:
        sigs = sigs.union(get_functions(u.left_side))
        sigs = sigs.union(get_functions(u.right_side))
    if len(sigs) > 1:
        raise Exception('Can only handle one function symbol that is AC')
    ac_symbol = next(iter(sigs))

    U = delete_trivial(U)

    if occurs_check(U):
        return False # TODO: return set()

    if function_clash(U):
        return False # TODO: return set()

    # Send the problem to the diophantine solver
    delta=convert_eq(U, ac_symbol)

    return set(delta)
