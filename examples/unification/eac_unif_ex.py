#eac_unif_ex.py
from algebra import Function, Equation, Variable
from Unification.eac_unif import eac_unif

exp = Function("exp", 2)
x = Variable("x")
y = Variable("y")
w = Variable("w")
t = exp(x,y)
t2 = exp(x, w)
e1 = Equation(t,t2)
U = set()
U.add(e1)
z = Variable("z")
g = Function("g", 2)
t3 = g(z,z)
t4 = g(w,w)
e2 = Equation(t3, t4)
U.add(e2)
eac_unif(U)

u = Variable("u")
v = Variable("v")
t3 = exp(v, w)
t4 = g(x, y)
e3 = Equation(u, t3)
e4 = Equation(u, t4)
U = set()
U.add(e3)
U.add(e4)
eac_unif(U)

exp = Function("exp", 2)
x = Variable("x")
y = Variable("y")
w = Variable("w")
u = Variable("u")
v = Variable("v")
t5 = exp(x, y)
t6 = exp(v, w)
e5 = Equation(u, t5)
e6 = Equation(u, t6)
U = set()
U.add(e5)
U.add(e6)
eac_unif(U)

exp = Function("exp", 2)
x = Variable("x")
y = Variable("y")
w = Variable("w")
u = Variable("u")
v = Variable("v")
t5 = exp(x, y)
t6 = exp(v, w)
e5 = Equation(u, t5)
e6 = Equation(u, t6)
U = set()
U.add(e6)
U.add(e5)
eac_unif(U)

exp = Function("exp", 2)
x = Variable("x")
y = Variable("y")
w = Variable("w")
u = Variable("u")
v = Variable("v")
t5 = exp(x, y)
t6 = exp(v, w)
e5 = Equation(u, t6)
e6 = Equation(v, t5)
U = set()
U.add(e5)
U.add(e6)
eac_unif(U)