"""
The listing module is responsible for defining
a list symbolically. Also contains common
computations on lists.
"""
from symcollab.algebra import Constant, Function, Variable
from symcollab.rewrite import RewriteRule, RewriteSystem
from .inductive import Inductive, TheorySystem
from .nat import Nat

__all__ = ['Listing']

@Inductive
class Listing(TheorySystem):
    nil = Constant("nil")
    cons = Function("cons", 2)

# Fix domain_sort of cons to take
# anything as its first argument
Listing.cons.domain_sort = [None, Listing.sort]

# Variables for later rules
_element = Variable("element")
_list = Variable("alist", sort=Listing.sort)
_list2 = Variable("blist", sort=Listing.sort)

# Repeat
_count = Variable("n", sort=Nat.sort)
repeat = Function("repeat", 2, domain_sort=[None, Nat.sort], range_sort=Listing.sort)
Listing.define(
    repeat,
    RewriteSystem({
        RewriteRule(repeat(_element, Nat.zero), Listing.nil),
        RewriteRule(repeat(_element, Nat.S(_count)), Listing.cons(_element, repeat(_element, _count)))
    })
)

# Length
length = Function("length", 1, domain_sort=Listing.sort, range_sort=Nat.sort)
Listing.define(
    length,
    RewriteSystem({
        RewriteRule(length(Listing.nil), Nat.zero),
        RewriteRule(length(Listing.cons(_element, _list)), Nat.S(length(_list)))
    })
)

# Extends
extend = Function("extend", 2, domain_sort=Listing.sort, range_sort=Listing.sort)
Listing.define(
    extend,
    RewriteSystem({
        RewriteRule(extend(Listing.nil, _list2), _list2),
        RewriteRule(extend(Listing.cons(_element, _list), _list2), Listing.cons(_element, extend(_list, _list2)))
    })
)

# Head
_default = Variable("default")
head = Function("head", 2, domain_sort=[None, Listing.sort])
Listing.define(
    head,
    RewriteSystem({
        RewriteRule(head(_default, Listing.nil), _default),
        RewriteRule(head(_default, Listing.cons(_element, _list)), _element)
    })
)

# Tail
# TODO: Diagnose this one...
# tail = Function("tail", 1, domain_sort=Listing.sort, range_sort=Listing.sort)
# Listing.define(
#     tail,
#     RewriteSystem({
#         RewriteRule(tail(Listing.nil), Listing.nil),
#         RewriteRule(tail(Listing.cons(_element, _list)), _list)
#     })
# )

# TODO: Create index function that makes use of optional
