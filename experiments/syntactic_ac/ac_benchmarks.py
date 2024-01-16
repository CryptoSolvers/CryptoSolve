#!/usr/bin/env python3
"""
Set of equations used to benchmark
AC unification algorithms
"""
from symcollab.algebra import Function, Variable, Equation

__all__ = ['benchmarks']

# Setup the variables and AC function
# NOTE: v is reserved as fresh variables
f = Function("f", 2)
w = Variable("w"); w1 = Variable("w1")
x = Variable("x"); x1 = Variable("x1")
y = Variable("y"); y1 = Variable("y1")
z = Variable("z"); z1 = Variable("z1")

benchmarks = (
    # 1. x + y + z = x1 + y1 + z1
    # (265 solutions)
    {Equation(f(x, f(y, z)), f(x1, f(y1, z1)))},
    # 2. w + x + y + z = w1 + x1 + y1 + z1
    # (41503 solutions)
    {Equation(f(w, f(x, f(y, z))), f(w1, f(x1, f(y1, z1))))},
    # 3. x + y + z = x1 + y1
    # (25 solutions)
    {Equation(f(x, f(y, z)), f(x1, y1))},
    # 4. x + y + z = x1 + x1
    # (45 solutions)
    {Equation(f(x, f(y, z)), f(x1, x1))},
    # 5. w + x + y + z = w1 + x1
    # (79 solutions)
    {Equation(f(w, f(x, f(y, z))), f(w1, x1))},
    # 6. w + x + y + z = w1 + w1
    # (809 solutions)
    {Equation(f(w, f(x, f(y, z))), f(w1, w1))},
    # 7. w + x + y + z = w1 + x1 + x1
    # (13703 solutions)
    {Equation(f(w, f(x, f(y, z))), f(w1, f(x1, x1)))},
    # 8. w + x + y + z = w1 + x1 + y1
    # (2161 solutions)
    {Equation(f(w, f(x, f(y, z))), f(w1, f(x1, y1)))},
    # 9. w + w + y + z = w1 + x1
    # (61 solutions)
    {Equation(f(w, f(w, f(y, z))), f(w1, x1))},
    # 10. w + w + y + z = w1 + w1 + x1
    # (69 solutions)
    {Equation(f(w, f(w, f(y, z))), f(w1, f(w1, x1)))},
    # 11. w + w + y + z = w1 + w1 + w1 
    # (101 solutions)
    {Equation(f(w, f(w, f(y, z))), f(w1, f(w1, w1)))},
    # 12. w + w + y + z = w1 + y1 + z1
    # (2901 solutions)
    {Equation(f(w, f(w, f(y, z))), f(w1, f(y1, z1)))},
    # 13. w + w + w + y = w1 + y1 + z1
    # (7029 solutions)
    {Equation(f(w, f(w, f(w, y))), f(w1, f(y1, z1)))},
    # 14. w + w + w + y = w1 + w1 + x1
    # (47 solutions)
    {Equation(f(w, f(w, f(w, y))), f(w1, f(w1, x1)))},
    # 15. w + w + w + w = w1 + x1 + y1 
    # (32677 solutions)
    {Equation(f(w, f(w, f(w, w))), f(w1, f(x1, y1)))}
)
