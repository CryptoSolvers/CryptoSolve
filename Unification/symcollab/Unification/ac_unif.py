#!/usr/bin/env python3
"""
#Elementary ACU-unification for single term pair

####################################################
To-Do:
-- [IN PROGRESS] Add free function symbols
-- Add ACU, ACUI, and AG  unification
-- Allow more than one AC symbol
-- Test the solver and AC solutions
"""
from collections import Counter
from copy import deepcopy
from itertools import product
from typing import Set, Dict, Tuple, List, Optional

import functools

from sympy.solvers.diophantine.diophantine import diop_linear
from sympy.core.sorting import default_sort_key
from sympy import symbols
import sympy

from symcollab.algebra import Equation, get_vars, Variable, SubstituteTerm, Constant, Term, Function
from symcollab.Unification.common import (
    delete_trivial, occurs_check, function_clash
)
from symcollab.Unification.unif import unif as syntactic_unification
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


def flatten_term(t: Term, ac_symbol: Function) -> List[Term]:
    """
    Takes a term that's rooted with an ac_symbol and flattens
    it and returns its list of subarguments.

    Parameters
    ----------
    t : Term
        Term to flatten.
    ac_symbol : Function
        Root function that should be treated as an associative
        commutative function for flattening.

    Examples
    ========
    >>> flatten_term(f(f(x, g(x)), g(g(f(x,x)))), f)
    [x, g(x), g(g(f(x, x)))]
    """
    if isinstance(t, (Constant, Variable)):
        return [t]
    
    if t.function != ac_symbol:
        return [t]
    
    l : List[Term] = []
    for ti in t.arguments:
        l = l + flatten_term(ti, ac_symbol)
    
    return l


def flatten_equation(eq: Equation, ac_symbol: Function) -> Tuple[List[Term], List[Term]]:
    """
    Takes an equation that's rooted with an ac_symbol and flattens
    each side.

    Parameters
    ----------
    eq : Equation
        Equation to flatten.
    ac_symbol : Function
        Root function that should be treated as an associative
        commutative function for flattening.

    Examples
    ========
    >>> flatten_equation(Equation(f(f(x, g(x)), x), f(g(x), g(x))), f)
    ([x, g(x), x], [g(x), g(x)])
    """
    return flatten_term(eq.left_side, ac_symbol), flatten_term(eq.right_side, ac_symbol)

def fresh_variable(existing_vars: Set[Variable], prefix : str = "z") -> Variable:
    """
    Returns a new variable that doesn't already
    exist in the existing_vars set.
    Note: Does not modify existing_vars
    """
    new_var = Variable(prefix)
    while new_var in existing_vars:
        new_var = Variable(new_var.symbol + "_1")
    return new_var

def n_fresh_variables(existing_vars: Set[Variable], n: int, prefix: str = "z") -> List[Variable]:
    """
    Generates multiple fresh varables.
    Note: Does not modify existing_vars
    """
    existing_vars = deepcopy(existing_vars)
    new_vars: List[Variable] = []
    for _ in range(n):
        v = fresh_variable(existing_vars, prefix)
        existing_vars.add(v)
        prefix = v.symbol
        new_vars.append(v)
    return new_vars


def generate_basis_table(basis_vector):
    """
    From a basis vector solution of a diophantine
    equation, generate a basis table 
    that satisfy the following constraints.

    (1) All entries are non-negative with respect to the basis vector
    (2) The sum of every column is greater than zero

    This is implemented as a generator, so you can generate infinite
    basis tables.
    """
    free_symbols = list(functools.reduce(lambda c, n: c.union(n), (x.free_symbols for x in basis_vector)))
    possible_instantiations = infinite_sequences(len(free_symbols))
    next(possible_instantiations) # Throw away all zero instantation
    basis_table = []
    while True:
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
                    vector.append(int(entry))
                # Check validity
                valid = all((entry >= 0 for entry in vector))

            # Add row to the table
            basis_table.append(vector)

            # Check to see if table is finished
            # A table is finished if the sum of every column is greater than 0
            finish_generating = all(sum(col) > 0 for col in zip(*basis_table))
        
        yield basis_table

def vars_from_equations(U: Set[Equation]):
    """
    Return all variables from a
    set of equations
    """
    ALL_VARS = set()
    for e in U:
        LS = get_vars(e.left_side, unique=True)
        RS = get_vars(e.right_side, unique=True)
        ALL_VARS = ALL_VARS.union(LS).union(RS)
    return ALL_VARS

def stickel_method(U: Set[Equation], ac_symbol: Function) -> SubstituteTerm:
    """
    Convert a set of term equations into a single
    linear homogeneous diophantine equation
    and solve it using stickel's method.
    
    The current diophantine solver uses Z3.
    """
    # Gather all variables for fresh var calculation
    ALL_VARS = vars_from_equations(U)
    generalized_term : Dict[Variable, Term] = dict()

    def generalize_term(t: Term) -> Variable:
        """
        Returns a generalized variable for every
        term that's not a variable.
        """
        vt = t
        if not isinstance(t, Variable):
            if t not in generalized_term:
                vt = fresh_variable(ALL_VARS)
                ALL_VARS.add(vt)
                generalized_term[vt] = t
            else:
                vt = generalized_term[t]
        return vt

    var_count = Counter()
    # Go through each equation
    for e in U:
        LS, RS = flatten_equation(e, ac_symbol)

        # Generalize left and right sides
        LS_VARS = [generalize_term(t) for t in LS]
        RS_VARS = [generalize_term(t) for t in RS]

        # Calculate multiplicity
        VARS_IN_EQ = set(LS_VARS).union(set(RS_VARS))
        for x in VARS_IN_EQ:
            num = LS_VARS.count(x) - RS_VARS.count(x)
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

    # Generate the basis table
    basis_table = next(generate_basis_table(basis_vector))

    # Create variables representing each row
    row_vars = n_fresh_variables(ALL_VARS, len(basis_table))
    ALL_VARS = ALL_VARS.union(set(row_vars))

    # Craft substitution from basis table
    sigma = SubstituteTerm()
    for column, sympy_var in enumerate(sympy_ordering):
        term = None
        for i, row in enumerate(basis_table):
            if row[column] == 0:
                continue
            row_var = row_vars[i]
            for _ in range(row[column]):
                if term is None:
                    term = row_var
                else: # z_2 + z_4
                    term = ac_symbol(term, row_var)
        sigma.add(var_map[sympy_var], term)

    # [TODO] [IN PROGRESS] Unify variables in the generalized terms with
    # their counterparts in the original terms.
    # new_eqs = {Equation(lhs, rhs) for lhs, rhs in generalized_term.items()}
    # generalize_sigma = syntactic_unification(new_eqs)


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
def ac_unify(U: Set[Equation], ac_symbol: Function):

    # Return no unifiers for a set of empty equations
    if len(U) == 0:
        return False # TODO: return set()

    U = delete_trivial(U)

    if occurs_check(U):
        return False # TODO: return set()

    if function_clash(U):
        return False # TODO: return set()

    # Send the problem to the diophantine solver
    delta = stickel_method(U, ac_symbol)

    return set(delta)
