"""Example file for Propositional Logic Resolution."""
from symcollab.algebra import Variable
from symcollab.theories.proposition import Implies, And, Or
from symcollab.theories.prop_logic import Clause, prop_dpp, \
    proposition_to_clause, Prop, Not

# Example using the DPP Resolution Algorithm
P = Variable("P", sort=Prop.sort)
Q = Variable("Q", sort=Prop.sort)
R = Variable("R", sort=Prop.sort)
S = Variable("S", sort=Prop.sort)
C1 = Clause("C1", {Not(P), Q})
C2 = Clause("C2", {Not(Q), Not(R), S})
C3 = Clause("C3", {P})
C4 = Clause("C4", {R})
C5 = Clause("C5", {Not(S)})
print(prop_dpp({C1, C2, C3, C4, C5}, {P, Q, R, S}))

# Example converting a proposition into a clause
a = Variable("a", sort=Prop.sort)
b = Variable("b", sort=Prop.sort)
c = Variable("c", sort=Prop.sort)
t = Implies(And(And(Or(a, b), Implies(a, c)), Implies(b, c)), c)
print(proposition_to_clause(t))
