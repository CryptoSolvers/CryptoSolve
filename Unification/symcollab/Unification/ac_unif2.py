#Elementary ACU-unification for single term pair

####################################################
#To-Do:
#-- Add ACU, ACUI, and AG  unification
#-- Fix the conversion from the diophantine solver
#-- Add free function symbols
#-- Allow more than one AC symbol
#-- Test the solver and AC solutions

#!/usr/bin/env python3
from collections import Counter
from copy import deepcopy
from typing import Set
import numpy as np # type: ignore
from z3 import Int, Solver
from symcollab.algebra import Equation, FuncTerm, get_vars, Variable


#convert a set of term equations into a single
#linear homogeneous diophantine equation
def convert_eq(U: Set[Equation]):
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
        var_string = x.symbol + "_0"
        z3_var = Int(var_string)

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
def ac_unify2(U: Set[Equation]):

    # Return no unifiers for a set of empty equations
    if len(U) == 0:
        return set()

    # Remove trivial equations
    for e in U:
        if e.right_side == e.left_side:
            U.remove(e)

    #Occurs Check
    for e in U:
        if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
            if e.left_side in e.right_side:
                print('Occurs Check')
                return set()
        if isinstance(e.right_side, Variable) and isinstance(e.left_side, FuncTerm):
            if e.right_side in e.left_side:
                print('Occurs Check')
                return set()

    #Function Clash
    for e in U:
        if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
            if e.left_side.function.symbol != e.right_side.function.symbol:
                print('Function Clash')
                return set()

    # Send the problem to the diophantine solver
    delta=convert_eq(U)

    return set(delta)
