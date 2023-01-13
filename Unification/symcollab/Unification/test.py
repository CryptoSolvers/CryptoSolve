from symcollab.algebra import *
from symcollab.Unification.ac_unif import ac_unify

x1 = Variable("x1")
x2 = Variable("x2")
x3 = Variable("x3")
y1 = Variable("y1")
y2 = Variable("y2")
y3 = Variable("y3")
y4 = Variable("y4")

f = Function("f", 2)

prob = Equation(
    f(x1, f(x1, f(x2, x3))),
    f(y1, f(y2, f(y3, y4)))
)
