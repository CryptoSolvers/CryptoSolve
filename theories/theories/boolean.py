"""
The Boolean module is responsible for defining
a symbolic bool (true/false) and properties
of them.
"""
from copy import deepcopy
from algebra import Constant, Function, FuncTerm, Term, Variable
from rewrite import RewriteRule, RewriteSystem
from .inductive import Inductive

__all__ = ['Boolean']

@Inductive
class Boolean:
    # Core Definition
    trueb = Constant("true")
    falseb = Constant("false")

    # Unary Functions
    neg = Function("neg", 1)

    # Binary Functions
    andb = Function("andb", 2)
    orb = Function("orb", 2)

##
# Rules
##

# Variables for later rules
_n = Variable("n", sort=Boolean.sort)

# Negation Rules
Boolean.add_rules({
    RewriteRule(Boolean.neg(Boolean.trueb), Boolean.falseb),
    RewriteRule(Boolean.neg(Boolean.falseb), Boolean.trueb)
})

# And Rules
Boolean.add_rules({
    RewriteRule(Boolean.andb(Boolean.trueb, _n), _n),
    RewriteRule(Boolean.andb(Boolean.falseb, _n), Boolean.falseb)
})

# Or Rules
Boolean.add_rules({
    RewriteRule(Boolean.orb(Boolean.trueb, _n), Boolean.trueb),
    RewriteRule(Boolean.orb(Boolean.falseb, _n), _n)
})

def from_bool(x: bool) -> Term:
    """Converts a bool to a Boolean."""
    return Boolean.trueb if x else Boolean.falseb

def to_bool(x: Term) -> bool:
    """Converts a Boolean to an bool."""
    if not isinstance(x, FuncTerm) or x != Boolean.trueb or x != Boolean.falseb:
        raise ValueError("to_bool function expects a simplified Boolean.")
    return x == Boolean.trueb

setattr(Boolean, 'from_bool', from_bool)
setattr(Boolean, 'to_bool', to_bool)
