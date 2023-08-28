#!/usr/bin/env python3
from collections import Counter
from typing import Set
from symcollab.algebra import Constant, Function, Variable, Equation, SubstituteTerm, get_vars
from symcollab.Unification.new_syntactic_ac_unification import synt_ac_unif
from symcollab.Unification.equiv import syntactic_equal

from common import print_unique_sol, print_failures, check_simple_ac_unifier

def run_example(label: str, equations: Set[Equation]):
    print(label)
    print(equations)
    # synt_ac_unif(set of equations, ac_symbol, single solution?)
    sol = synt_ac_unif(equations, f, False)
    print_unique_sol(sol)
    print_failures(equations, sol, check_simple_ac_unifier)
    print("")

#Setup the variables and AC function
f = Function("f", 2); g = Function("g", 2)
v = Variable("v"); w = Variable("w")
x = Variable("x"); y = Variable("y")
z = Variable("z")
v1 = Variable("v1"); w1 = Variable("w1")
x1 = Variable("x1"); y1 = Variable("y1")
z1 = Variable("z1")
a = Constant("a"); b = Constant("b")


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

# [PASS w/S1 Bound] Four distinct variables on each side
lhs = f(w, f(x, f(y, z)))
rhs = f(w1, f(x1, f(y1, z1)))
e = Equation(lhs, rhs)
U = {e}
run_example("Example 4", U)

# [PASS w/S1 Bound] Five distinct variables on each side
lhs = f(v, f(w, f(x, f(y, z))))
rhs = f(v1, f(w1, f(x1, f(y1, z1))))
e = Equation(lhs, rhs)
U = {e}
run_example("Example 5", U)

"""
===================================
Test cases with duplicate variables
===================================
"""

# [PASS w/S2 bound] Duplicate variable on each side
lhs = f(x, x)
rhs = f(y, y)
e = Equation(lhs, rhs)
U = {e}
run_example("Example 6", U)


# [PASS w/S2 bound] Differing multiplicity with duplicate variables
lhs = f(x, x)
rhs = f(f(y,y),f(z,z))
e = Equation(lhs, rhs)
U = {e}
run_example("Example 7", U)

# [PASS w/S2 bound] Differing multiplicity of duplicate variables
lhs = f(x,f(x, x))
rhs = f(y, f(y, z))
e = Equation(lhs, rhs)
U = {e}
run_example("Example 8", U)

"""
======================
Testing associativity
======================
"""

# [PASS w/S1 bound] Left associativity with 4 distinct variables
lhs = f(f(f(w, x), y), z)
rhs = f(f(f(w1, x1), y1), z1)
e = Equation(lhs, rhs)
U = {e}
run_example("Example 9", U)

# [PASS w/S1 bound] Mixed associativity with 5 distinct variables
lhs = f(f(f(v, w), x), f(y, z))
rhs = f(f(f(v1, w1), x1), f(y1, z1))
e = Equation(lhs, rhs)
U = {e}
run_example("Example 10", U)

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
run_example("Example 11", U)

# [PASS w/S1 bound] Four distinct variables on each side changing the order
lhs = f(w, f(x, f(y, z)))
rhs = f(y1, f(x1, f(z1, w1)))
e = Equation(lhs, rhs)
U = {e}
run_example("Example 12", U)

# [PASS w/S1+S2 bound] Three distinct variables (1 duplicate) on each side changing the order
lhs = f(w, f(w, f(y, z)))
rhs = f(y1, f(w1, f(z1, w1)))
e = Equation(lhs, rhs)
U = {e}
run_example("Example 13", U)


"""
=============================================
Testing both associativity and commutativity
=============================================
"""
# TODO

"""
=========================
Test cases with constants
=========================
"""
# [PASS] Constants cannot unify
lhs = a
rhs = b
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 14", U)

# [PASS] Constants within functions that cannot unify
lhs = f(a,a)
rhs = f(b,b)
e = Equation(lhs,rhs)
U = {e}
# run_example("Example 15", U)

# [PASS] Constants and Variables
lhs = f(x, a)
rhs = f(b, x1)
e = Equation(lhs,rhs)
U = {e}
# run_example("Example 16", U)


# [PASS] Constants and Variables, order swapped
lhs = f(a, x)
rhs = f(b, x1)
e = Equation(lhs,rhs)
U = {e}
# run_example("Example 17", U)

"""
=====================================
Test cases with free function symbols
=====================================
"""

# [PASS] Free function symbol with no internal variables
lhs = f(g(a, b), x)
rhs = f(g(a, b), x1)
e = Equation(lhs,rhs)
U = {e}
# run_example("Example 18", U)

# [PASS] Free function symbol with one variable within on one side
lhs = f(g(y, b), x)
rhs = f(g(a, b), x1)
e = Equation(lhs,rhs)
U = {e}
# run_example("Example 19", U)

# [PASS] Free function symbol with one variable within
lhs = f(g(y, b), x)
rhs = f(g(y1, b), x1)
e = Equation(lhs,rhs)
U = {e}
# run_example("Example 20", U)

# [PASS] Free function symbol with two variables within one side
lhs = f(g(a, b), x)
rhs = f(g(y, y1), x1)
e = Equation(lhs,rhs)
U = {e}
# run_example("Example 21", U)

# [PASS] Free function symbol with different varables within
lhs = f(g(y, a), x)
rhs = f(g(y1, b), x1)
e = Equation(lhs,rhs)
U = {e}
# run_example("Example 22", U)


# [PASS] Free function symbol on the outside
lhs = g(f(w,x),f(y,z))
rhs = g(f(w1,x1),f(y1,z1))
e = Equation(lhs,rhs)
U = {e}
# run_example("Example 23", U)

"""
===========================
Advanced test cases mixing
the above properties.
===========================
"""

# [PASS w/S1 bound] Four distinct variables on each side repeat of 4 with swapped nesting
lhs = f(f(x,f(x,y)),w)
rhs = f(f(x1,f(y1,z1)),w1)
e = Equation(lhs,rhs)
U = {e}
# run_example("Example 24", U)
