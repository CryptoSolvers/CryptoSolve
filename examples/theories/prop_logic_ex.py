"""Example file for Propositional Logic Resolution."""
from symcollab.algebra import Variable
from symcollab.theories import (
    Imp, And, Or, dpll,
    literals, Not, Relation, nnf
)

# Example using the DPP Resolution Algorithm
P = Relation("P", 0)()
Q = Relation("Q", 0)()
R = Relation("R", 0)()
S = Relation("S", 0)()
C1 = [Not(P), Q]
C2 = [Not(Q), Not(R), S]
C3 = [P]
C4 = [R]
C5 = [Not(S)]
print(dpll([C1, C2, C3, C4, C5]))

# Example converting a proposition into a clause
a = Relation("a", 0)()
b = Relation("b", 0)()
c = Relation("c", 0)()
t = Imp(And(And(Or(a, b), Imp(a, c)), Imp(b, c)), c)
print(literals(nnf(t)))
