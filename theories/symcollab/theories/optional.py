"""
Optional type allows one to have a
None type when something is undefined
instead of having terms that don't rewrite.
"""
from symcollab.algebra import Constant, Function
from .inductive import TheorySystem, Inductive

@Inductive
class Optional(TheorySystem):
    none = Constant("None")
    some = Function("some", 1)

# Fix type for some
Optional.some.domain_sort = None

