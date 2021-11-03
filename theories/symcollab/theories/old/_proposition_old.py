"""
Propositions are statements that can be true or false.
They are a higher level of abstraction from booleans which
can be computed.

The rewrite rules here are used to convert propositions
into Conjunctive Form.

Since there's currently no associativity implemented,
it does not simplify to a normal form of a term.

Inspired by "Implementing a Propositional Logic Theorem Prover in Haskell"
by Laurence Edward Day
"""
from symcollab.algebra import Function, Variable
from symcollab.rewrite import RewriteRule, RewriteSystem
from .inductive import Inductive, TheorySystem

@Inductive
class Prop(TheorySystem):
    pass

A = Variable("A", sort=Prop.sort)
B = Variable("B", sort=Prop.sort)
C = Variable("C", sort=Prop.sort)

Not = Function("not", 1, domain_sort=Prop.sort, range_sort=Prop.sort)
Prop.define(
    Not,
    RewriteSystem({
        RewriteRule(Not(Not(A)), A)
    })
)

And = Function("and", 2, domain_sort=Prop.sort, range_sort=Prop.sort)
Prop.define(
    And,
    RewriteSystem({
        RewriteRule(And(A, A), A),
    })
)

Or = Function("or", 2, domain_sort=Prop.sort, range_sort=Prop.sort)
Prop.define(
    Or,
    RewriteSystem({
        RewriteRule(Or(A, A), A),
    })
)

Implies = Function("implies", 2, domain_sort=Prop.sort, range_sort=Prop.sort)
Prop.define(
    Implies,
    RewriteSystem({
        RewriteRule(Implies(A, B), Or(Not(A), B))
    })
)

Iff = Function("iff", 2, domain_sort=Prop.sort, range_sort=Prop.sort)
Prop.define(
    Iff,
    RewriteSystem({
        RewriteRule(
            Iff(A, B),
            And(Implies(A, B), Implies(B, A))
        )
    })
)

# Other rules to convert things to conjunctive normal form
Prop.rules.extend(RewriteSystem({
    # De Morgan's Laws
    RewriteRule(Not(Or(A, B)), And(Not(A), Not(B))),
    RewriteRule(Not(And(A, B)), Or(Not(A), Not(B))),

    # Algebraic Distribution
    RewriteRule(Or(A, And(B, C)), And(Or(A, B), Or(A, C))),
    RewriteRule(Or(And(A, B), C), And(Or(A, C), Or(B, C))),

    # Associativity Rules
    RewriteRule(Or(Or(A, B), C), Or(A, Or(B, C))),
    RewriteRule(And(And(A, B), C), And(A, And(B, C))),

    # Absorption Laws
    RewriteRule(And(A, Or(A, B)), A),
    RewriteRule(And(Or(A, B), A), A),
    RewriteRule(And(B, Or(A, B)), B),
    RewriteRule(And(Or(A, B), B), B)
}))
