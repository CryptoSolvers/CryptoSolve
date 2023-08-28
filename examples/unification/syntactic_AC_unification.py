#!/usr/bin/env python3
from collections import Counter
from typing import Set
from symcollab.algebra import Constant, Function, Variable, Equation, SubstituteTerm, get_vars
from symcollab.Unification.syntactic_ac_unification import synt_ac_unif

from common import check_simple_ac_unifier, print_failures, print_sol

def run_example(label: str, equations: Set[Equation]):
    print(label)
    print(equations)
    # synt_ac_unif(set of equations, single solution?)
    sol = synt_ac_unif(equations, False)
    print_sol(sol)
    print_failures(equations, sol, check_simple_ac_unifier)
    print("")

#Setup the variables and AC function
f = Function("f", 2)
v = Variable("v"); w = Variable("w")
x = Variable("x"); y = Variable("y")
z = Variable("z")
v1 = Variable("v1"); w1 = Variable("w1")
x1 = Variable("x1"); y1 = Variable("y1")
z1 = Variable("z1")

"""
=======================================
Test cases with only distinct variables
=======================================
"""

# [PASS] One distinct variable on each side
lhs = x
rhs = x1
e = Equation(lhs, rhs)
U = {e}
run_example("Example 1", U)

# [PASS] Two distinct variables on each side
lhs = f(x, y)
rhs = f(x1, y1)
e = Equation(lhs, rhs)
U = {e}
run_example("Example 2", U)


# [PASS] Three distinct variables on each side
lhs = f(x, f(y, z))
rhs = f(x1, f(y1, z1))
e = Equation(lhs, rhs)
U = {e}
run_example("Example 3", U)

# [PASS] Four distinct variables on each side
lhs = f(w, f(x, f(y, z)))
rhs = f(w1, f(x1, f(y1, z1)))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 4", U)

# [PASS] Five distinct variables on each side
lhs = f(v, f(w, f(x, f(y, z))))
rhs = f(v1, f(w1, f(x1, f(y1, z1))))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 5", U)

"""
===================================
Test cases with duplicate variables
===================================
"""

# [PASS] Duplicate variable on each side
lhs = f(x, x)
rhs = f(y, y)
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 6", U)


# [PASS] Differing multiplicity with duplicate variables
lhs = f(x, x)
rhs = f(f(y,y),f(z,z))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 7", U)

# [PASS] Differing multiplicity of duplicate variables
lhs = f(x,f(x, x))
rhs = f(y, f(y, z))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 8", U)


"""
======================
Testing associativity
======================
"""

# [PASS] Left associativity with 4 distinct variables
lhs = f(f(f(w, x), y), z)
rhs = f(f(f(w1, x1), y1), z1)
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 9", U)

# [PASS] Mixed associativity with 5 distinct variables
lhs = f(f(f(v, w), x), f(y, z))
rhs = f(f(f(v1, w1), x1), f(y1, z1))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 10", U)

"""
=====================
Testing commutativity
=====================
"""
# [PASS] Three distinct variables on each side flipping the order
lhs = f(x, f(y, z))
rhs = f(z1, f(y1, x1))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 11", U)

# [PASS] Four distinct variables on each side changing the order
lhs = f(w, f(x, f(y, z)))
rhs = f(y1, f(x1, f(z1, w1)))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 12", U)

# [PASS] Three distinct variables (1 duplicate) on each side changing the order
lhs = f(w, f(w, f(y, z)))
rhs = f(y1, f(w1, f(z1, w1)))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 13", U)


"""
=============================================
Testing both associativity and commutativity
=============================================
"""
# TODO

"""
===========================
Advanced test cases mixing
the above properties.
===========================
"""

# [PASS] Four distinct variables on each side repeat of 4 with swapped nesting
lhs = f(f(x,f(x,y)),w)
rhs = f(f(x1,f(y1,z1)),w1)
e = Equation(lhs,rhs)
U = {e}
# run_example("Example 14", U)
