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
"""
from collections import Counter
from copy import deepcopy
from itertools import product
from typing import Set, Optional

import functools

import numpy as np # type: ignore

from sympy.solvers.diophantine.diophantine import diop_linear
from sympy import symbols

from symcollab.algebra import Equation, FuncTerm, get_vars, Variable, SubstituteTerm, Constant, Term, Function
from symcollab.Unification.common import *


def within_equation(t: Term, e: Equation):
    """
    Returns True if term t appears
    within either the left side or right
    side of equation e.
    """
    for e_part in [e.left_side, e.right_side]:
        # Split check based on Constant/Variable and FuncTerms
        if isinstance(e_part, (Constant, Variable)):
            if t == e_part:
                return True
        if isinstance(e_part, FuncTerm):
            if t in e_part:
                return True
    return False

def within_equations(t: Term, equations: Set[Equation]):
    """
    Returns True if term t appears
    within any of the equations provided.
    """
    return any(
        within_equation(t, e) for e in equations
    )

def variable_replacement(equations, orignal_equations):
    """
    Source; Boudet 1990
    Variable Replacement Rule

    If x and y appear in P and either
    y occurs in the original problem or
    x does not occur in the original problem then

    P∪{x=y} => P{x -> y}∪{x=y}

    Returns original equations and sigma
    if the rule cannot be matched.
    """
    matched_equation: Optional[Equation] = None

    for equation in equations:
        lhs = equation.left_side
        rhs = equation.right_side

        # Make sure both sides are variables
        if not isinstance(lhs, Variable) or not isinstance(rhs, Variable):
            continue

        # Original problem check:
        # Either y occurs in the OG problem or x does not occur in the OG problem
        og_problem_check = \
            within_equations(rhs, orignal_equations) or not within_equations(lhs, orignal_equations)

        if not og_problem_check:
            continue

        # Make sure that both the left hand side
        # and right hand side of the equation exist
        # in any of the other equations.
        loccurs = within_equations(lhs, equations - {equation})
        roccurs = within_equations(rhs, equations - {equation})

        # If both sides are found, we're proceeding with this equation
        # for the rest of the rule.
        if loccurs and roccurs:
            matched_equation = equation
            break

    # If no equations are found return early
    if matched_equation is None:
        return equations


    # Create the new substitution
    new_sub = SubstituteTerm()
    new_sub.add(matched_equation.left_side, matched_equation.right_side)

    # Apply the new substitution to the set of equations
    new_equations = set()
    for equation in equations - {matched_equation}:
        new_equations.add(Equation(
            equation.left_side * new_sub,
            equation.right_side * new_sub
        ))

    # Add the matched equation to the result
    new_equations.add(matched_equation)

    return new_equations


def remove_rule(equations, original_equations):
    """
    Source: Boudet 1990
    Remove rule:

    If x not in the original problem and
    x not in either s or P then
    {x=s}∪P => P

    Note: Removes useless equations
    that do not satisfy the condition 4
    of the definition of the dag solved form.
    """
    matched_equation = None
    for equation in equations:
        lhs = equation.left_side
        rhs = equation.right_side

        if not isinstance(lhs, Variable):
            continue

        # Check x \not\in V(s)
        if isinstance(rhs, (Constant, Variable)) and lhs == rhs:
            continue
        if isinstance(rhs, FuncTerm) and lhs in rhs:
            continue

        # Check x \not\in V(P^0)
        if within_equations(lhs, original_equations):
            continue

        # Check x \not\in V(P)
        if within_equation(lhs, equations - {equation}):
            continue

        matched_equation = equation
        break

    if matched_equation is None:
        return equations

    return equations - {matched_equation}


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
    variables = []
    for x, count in var_count.items():
        # Construct Z3 variable
        sympy_var = symbols(x.symbol + "_0", integer=True, positive=True)

        # Store variables to associate ordering with basis vector
        variables.append(x)

        # Construct part of expression
        sympy_expression += count * sympy_var

    print("Diophantine Equation:", sympy_expression)
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
    for column in range(len(variables)):
        term = None
        for i, row in enumerate(basis_table):
            row_var = Variable("z_" + str(i)) # TODO: Make sure z_ isnt taken...
            if row[column] > 0:
                for _ in range(row[column]):
                    if term is None:
                        term = row_var
                    else: # z_2 + z_4
                        term = ac_symbol(term, row_var)
        sigma.add(variables[column], term)

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
def ac_unify(U: Set[Equation]):

    # Return no unifiers for a set of empty equations
    if len(U) == 0:
        return False # TODO: return set()

    sigs = set()
    for u in U:
        sigs = sigs.union(get_functions(u.left_side))
        sigs = sigs.union(get_functions(u.right_side))
    if len(sigs) > 1:
        raise Exception('Can only handle one AC symbol')
    ac_symbol = next(iter(sigs))

    U = delete_trivial(U)

    if occurs_check(U):
        return False # TODO: return set()

    if function_clash(U):
        return False # TODO: return set()

    # Send the problem to the diophantine solver
    delta=convert_eq(U, ac_symbol)

    return set(delta)
