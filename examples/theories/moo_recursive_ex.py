#!/usr/bin/env python3
"""
A thought experiment on how to define
recursive MOOs.
"""
from algebra import Constant, Function, Variable
from rewrite import RewriteRule, RewriteSystem, normal
from xor import xor
import theories.nat as nat

C = Function("C", 1, domain_sort=nat.nat_sort)
P = Function("P", 1, domain_sort=nat.nat_sort)
f = Function("f", 1)
IV = Constant("IV")
n = Variable("n", sort=nat.nat_sort)

r0 = RewriteRule(C(nat.zero), IV)
rn = RewriteRule(C(nat.S(n)), f(xor(P(nat.S(n)), C(n))))
moo_system = RewriteSystem({r0, rn})
print("Cipher Block Chaining:", moo_system)

three = nat.from_int(3)
print("Simplified form of the 3rd ciphertext:", normal(C(three), moo_system))
