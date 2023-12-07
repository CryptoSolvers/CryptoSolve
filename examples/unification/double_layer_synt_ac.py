#!/usr/bin/env python3
from collections import Counter
from typing import Set
from symcollab.algebra import Constant, Function, Variable, Equation, SubstituteTerm, get_vars
from symcollab.Unification.syntactic_ac_unif_3 import *
from symcollab.Unification.equiv import syntactic_equal

from common import print_unique_sol, print_failures, check_simple_ac_unifier, print_sol

"""
Associated with synctactic_ac_unif_3.py
"""

def run_example(label: str, equations: Set[Equation]):
    print(label)
    print(equations)
    # synt_ac_unif(set of equations, single solution?)
    sol = synt_ac_unif3(equations, False)
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


# [PASS w bound]Example Special
e = Equation(
    f(x, x),
    f(f(y,z),z)
)
U = {e}
# run_example("Example Special", U)

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
# run_example("Example 1", U)

# [PASS] Two distinct variables on each side
lhs = f(x, y)
rhs = f(x1, y1)
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 2", U)


# [PASS] Three distinct variables on each side
lhs = f(x, f(y, z))
rhs = f(x1, f(y1, z1))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 3", U)

# [FAIL] Four distinct variables on each side
# NOTE: Single solution flag passes
# NOTE: This actually terminates, it exhausts through 9 layers
# which takes a while
# Total Layers Computed: 9
# Total Solutions: 41503

# [Pass with bound of 5]
lhs = f(w, f(x, f(y, z)))
rhs = f(w1, f(x1, f(y1, z1)))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 4", U)

# [FAIL] Five distinct variables on each side
# NOTE: Single solutoin passes
# [Pass with bound of 5]
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
lhs = f(x, x)
rhs = f(y, y)
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 6", U)


# [FAIL] Differing multiplicity with duplicate variables
# NOTE: Single solution passes
# [Pass with 5 bound]
lhs = f(x, x)
rhs = f(f(y,y),f(z,z))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 7", U)

# [FAIL] Differing multiplicity of duplicate variables
# NOTE: Single solution passes
# [Pass with bound 5]
lhs = f(x,f(x, x))
rhs = f(y, f(y, z))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 8", U)


lhs = f(x, f(x, x))
rhs = f(y, f(y, y))
e = Equation(lhs, rhs)
U = {e}
run_example("Brandon10", U)

y2 = Variable("y2")
y3 = Variable("y3")
y4 = Variable("y4")
U = {
    Equation(x, f(y1, y2)),
    Equation(x, f(y3, y4)),
    Equation(z1, z1)
}
# run_example("AndrewSpecial10", U)

U = {
    Equation(x, f(y1, y2)),
    Equation(x, f(y3, y4)),
    Equation(y2, f(y1, y1))
}
# run_example("AndrewSpecial12", U)


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
lhs = f(x, f(y, z))
rhs = f(z1, f(y1, x1))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 11", U)

# [FAIL] Four distinct variables on each side changing the order
# NOTE: Single solution passes
# [Pass with bound of 5]
lhs = f(w, f(x, f(y, z)))
rhs = f(y1, f(x1, f(z1, w1)))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 12", U)

# [FAIL] Three distinct variables (1 duplicate) on each side changing the order
# NOTE: Single solution passes
# [Pass with bound of 5]
lhs = f(w, f(w, f(y, z)))
rhs = f(y1, f(w1, f(z1, w1)))
e = Equation(lhs, rhs)
U = {e}
# run_example("Example 13", U)





