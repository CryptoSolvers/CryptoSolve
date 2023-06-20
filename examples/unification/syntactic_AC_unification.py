#!/usr/bin/env python3
from collections import Counter
from typing import Set
from symcollab.algebra import Constant, Function, Variable, Equation, SubstituteTerm, get_vars
from symcollab.Unification.syntactic_ac_unification import *

def check_domain(problem: Equation, unifier: SubstituteTerm):
    left_vars = get_vars(problem.left_side, True)
    right_vars = get_vars(problem.right_side, True)
    original_variables = left_vars.union(right_vars)
    unifier_domain = set(unifier.domain())

    if len(original_variables - unifier_domain) > 0:
        return False

    return True

def check_substitution(problem: Equation, unifier: SubstituteTerm):
    left_vars = get_vars(problem.left_side)
    right_vars = get_vars(problem.right_side)

    left_substituted_solution = Counter()
    for l in left_vars:
        l_sub = l * unifier
        l_sub_vars = get_vars(l_sub)
        for lsv in l_sub_vars:
            left_substituted_solution[lsv] += 1

    right_substituted_solution = Counter()
    for r in right_vars:
        r_sub = r * unifier
        r_sub_vars = get_vars(r_sub)
        for rsv in r_sub_vars:
            right_substituted_solution[rsv] += 1

    if left_substituted_solution != right_substituted_solution:
        return False

    return True

def print_sol(sol: Set[SubstituteTerm]):
    if len(sol) == 0:
        print("No Solution\n")
        return
    print("First 5 solutions")
    print_num = min(len(sol), 5)
    sol_iter = iter(sol)
    for i in range(print_num):
        print("Solution", i, next(sol_iter))
    print("Total Solutions:", len(sol))

def print_failures(problem: Equation, sol: Set[SubstituteTerm]):
    num_domain_failures = 0
    num_substitution_failures = 0
    num_failures = 0
    for s in sol:
        if not check_domain(problem, s):
            # Could be variable renaming, so need to check substitution
            if not check_substitution(problem, s):
                num_domain_failures += 1
                num_failures += 1
            # Otherwise the solution is not complete
        elif not check_substitution(problem, s):
            num_substitution_failures += 1
            num_failures += 1

    print("Domain Failures:", num_domain_failures)
    print("Substitution Failures:", num_substitution_failures)
    print("Total Failures:", num_failures)


#Setup the variables and AC function
f = Function("f", 2)
w = Variable("w")
x = Variable("x")
y = Variable("y")
z = Variable("z")
a = Constant("a")
b = Constant("b")
w1 = Variable("w1")
x1 = Variable("x1")
y1 = Variable("y1")
z1 = Variable("z1")

# synt_ac_unif(set of equations, single solution?)

## AC Unification with only distinct variables

# Example 1: One distinct variable on each side (PASS)
e = Equation(x, x1)
U = {e}
sol = synt_ac_unif(U, False)
print_sol(sol)
print_failures(e, sol)
print("")

#Example 2: Two distinct variables on each side (PASS)
e = Equation(f(x, y), f(x1, y1))
U = {e}
sol = synt_ac_unif(U, False)
print_sol(sol)
print_failures(e, sol)
print("")

# Example 3: Three distinct variables on each side (PASS)
e = Equation(f(x, f(y, z)), f(x1, f(y1, z1)))
U = {e}
sol = synt_ac_unif(U, False)
print_sol(sol)
print_failures(e, sol)
print("")

# Example 4: Four distinct variables on each side (PASS with Stage 1 bound)
e = Equation(f(w, f(x, f(y, z))), f(w1, f(x1, f(y1, z1))))
U = {e}
sol = synt_ac_unif(U, False)
print_sol(sol)
print_failures(e, sol)
print("")

## Duplicate Variables

# Example 5: Duplicate variable on each side (PASS with stage 2/3 bound)
e = Equation(f(x,x), f(y,y))
U = {e}
sol = synt_ac_unif(U, False)
print_sol(sol)
print_failures(e, sol)
print("")


# Example 6: Differing multiplicity with duplicate variables (PASS with stage 1/2/3 bound)
e = Equation(
   f(x, x),
   f(f(y,y),f(z,z))
)
U = {e}
sol = synt_ac_unif(U, False)
print_sol(sol)
print_failures(e, sol)
print("")

# Example 7: Differing multiplicity of duplicate variables (PASS with stage 2/3 bound)
lhs = f(x,f(x, x))
rhs = f(y, f(y, z))
e = Equation(lhs, rhs)
U = {e}
sol = synt_ac_unif(U, False)
print_sol(sol)
print_failures(e, sol)
print("")
