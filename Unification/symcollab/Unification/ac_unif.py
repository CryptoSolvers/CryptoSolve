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
from typing import Set

import numpy as np # type: ignore
from z3 import Int, Solver

from symcollab.algebra import Equation, FuncTerm, get_vars, Variable
from symcollab.Unification.common import *


def within_equation(t: Term, e: Equation):
    """
    Returns True if term t appears
    within either the left side or right
    side of equation e.
    """
    for e_part in [e.left_side, e.right_side]:
        # Split check based on Constant/Variable and FuncTerms
        if isinstance(e2_part, (Constant, Variable)):
            if lhs == e2_part:
                return True
        if isinstance(e2_part, FuncTerm):
            if lhs in e2_part:
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




def convert_eq(U: Set[Equation]):
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
            if first:
                var_count[x] += num
            else:
                var_count[x] -= num
        first=False
    
    # Create the equation with variable coeficients
    # being the counts above    
    z3_solver = Solver()
    z3_variables = []
    z3_expression = 0
    for x, count in var_count.items():
        # Construct Z3 variable
        z3_var = Int(x.symbol + "_0")

        # Store variables to grab solution for later
        z3_variables.append(z3_var)

        # Add strictly positive constraint
        z3_solver.add(z3_var > 0)

        # Construct part of expression
        z3_expression += count * z3_var
    
    # Add completed diophantine equation as constraint
    z3_solver.add(z3_expression == 0)

    # Solve the system
    z3_solver.check()

    # Grab solutions from solver
    z3_model = z3_solver.model()
    z3_solutions = dict()
    for z3_var in z3_variables:
        z3_solutions[z3_var] = z3_model.eval(z3_var)

    # Print out resulting solutions
    print(z3_solutions)

    return set() # Temporary


#Assumes currently that we have a single AC-symbol
#need to update to allow other function symbols and cons
def ac_unify(U: Set[Equation]):

    # Return no unifiers for a set of empty equations
    if len(U) == 0:
        return False # TODO: return set()

    U = delete_trivial(U)

    if occurs_check(U):
        return False # TODO: return set()
    
    if function_clash(U):
        return False # TODO: return set() 

    # Send the problem to the diophantine solver
    delta=convert_eq(U)

    return set(delta)
