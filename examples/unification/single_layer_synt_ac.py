#!/usr/bin/env python3
from collections import Counter
from typing import Set
from symcollab.algebra import Constant, Function, Variable, Equation, SubstituteTerm, get_vars
from symcollab.Unification.syntactic_ac_unif_2 import *
from symcollab.Unification.equiv import syntactic_equal

from common import print_unique_sol, print_failures, check_simple_ac_unifier, print_sol

def run_example(label: str, equations: Set[Equation]):
    print(label)
    print(equations)
    # synt_ac_unif(set of equations, single solution?)
    sol = synt_ac_unif2(equations, False)
    # if len(sol) < 100:
    #     print_unique_sol(sol)
    # else:
    #     print_sol(sol)
    print_sol(sol)
    print_failures(equations, sol, check_simple_ac_unifier)
    print("")

#Setup the variables and AC function
f = Function("f", 2)
u = Variable("u"); u1 = Variable("u1")
# NOTE: v is reserved as fresh variables
w = Variable("w"); w1 = Variable("w1")
x = Variable("x"); x1 = Variable("x1")
y = Variable("y"); y1 = Variable("y1")
z = Variable("z"); z1 = Variable("z1")
a = Constant("a")
b = Constant("b")


# [PASS] Example Special
# Maude says there's one solution
# Our algorihtm returns two (which are the same)
# meaning that its equivalent
e = Equation(
    f(x, x),
    f(f(y,z),x)
)
U = {e}
# run_example("Example Special", U)

"""
=======================================
Test cases with only distinct variables
=======================================
"""

# [PASS] One distinct variable on each side
# Matches maude's solution exactly
lhs = x
rhs = x1
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 1", U)

# [PASS] Two distinct variables on each side
# Matches maude's solution
lhs = f(x, y)
rhs = f(x1, y1)
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 2", U)


# [PASS] Three distinct variables on each side
# Matches maude's solution (265 solutions)
lhs = f(x, f(y, z))
rhs = f(x1, f(y1, z1))
e = Equation(lhs, rhs)
U = {e}
run_example("Example 3", U)

# [PASS] Four distinct variables on each side
# Matches Maude's solutions (41503 solutions)
# Takes a long time if you don't place bounds
lhs = f(w, f(x, f(y, z)))
rhs = f(w1, f(x1, f(y1, z1)))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 4", U)

# [PASS w/Bound] Five distinct variables on each side
# Over 102000 solutions in Maude (Didn't wait for it to finish)
lhs = f(u, f(w, f(x, f(y, z))))
rhs = f(u1, f(w1, f(x1, f(y1, z1))))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 5", U)



"""
===================================
Test cases with duplicate variables
===================================
"""

# [PASS] Duplicate variable on each side
# Matches Maude's solution
lhs = f(x, x)
rhs = f(y, y)
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 6", U)


# [Pass with bound] Differing multiplicity with duplicate variables
# Maude says there's only a single solution
"""
More notes:
It seems that this is an example that can make better use from
pruning

First 5 solutions
Solution 0 {
v_1 ↦ f(y, y),
x ↦ f(v_1, y),
z ↦ f(y, y)
}
Solution 1 {
v_2 ↦ f(v_4, v_4),
x ↦ f(v_3, v_2),
y ↦ f(v_3, v_4),
z ↦ v_4
}
Solution 2 {
v_2 ↦ f(z, z),
x ↦ f(v_2, v_2),
y ↦ f(v_2, z)
}
Solution 3 {
x ↦ f(y, z),
y ↦ f(v_6, z),
z ↦ f(v_6, v_5)
}
Solution 4 {
x ↦ f(y, z),
y ↦ f(v_3, z)
}
Total Solutions: 54


"""
lhs = f(x, x)
rhs = f(f(y,y),f(z,z))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 7", U)

# [FAIL] Differing multiplicity of duplicate variables
# NOTE: Single solution passes
# Maude says there's 5 solutions
# [Pass with bound]
lhs = f(x,f(x, x))
rhs = f(y, f(y, z))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 8", U)

# Maude says there's only one solutoin
lhs = f(x, f(x, x))
rhs = f(y, f(y, y))
e = Equation(lhs, rhs)
U = {e}
# run_example("Brandon10", U)


"""
======================
Testing associativity
======================
"""

# [FAIL] Left associativity with 4 distinct variables
# NOTE: Single solution passes
# [Pass with bound 5]
lhs = f(f(f(w, x), y), z)
rhs = f(f(f(w1, x1), y1), z1)
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 9", U)

# [FAIL] Mixed associativity with 5 distinct variables
# NOTE: Single solution passes
# [Pass with bound of 5]
lhs = f(f(f(u, w), x), f(y, z))
rhs = f(f(f(u1, w1), x1), f(y1, z1))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 10", U)

"""
=====================
Testing commutativity
=====================
"""
# [PASS] Three distinct variables on each side flipping the order
# Maude says there's 265 solutions
lhs = f(x, f(y, z))
rhs = f(z1, f(y1, x1))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 11", U)

# [FAIL] Four distinct variables on each side changing the order
# Maude says there's 41503 solutions
# NOTE: Single solution passes
# [Pass with bound of 5]
lhs = f(w, f(x, f(y, z)))
rhs = f(y1, f(x1, f(z1, w1)))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 12", U)

# [FAIL] Three distinct variables (1 duplicate) on each side changing the order
# NOTE: Single solution passes
# Maude says theres 1489 solutions
# [Pass with bound of 5]
lhs = f(w, f(w, f(y, z)))
rhs = f(y1, f(w1, f(z1, w1)))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 13", U)

