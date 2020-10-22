#!/usr/bin/env python3
"""
A thought experiment on how to define
recursive MOOs.
"""
from algebra import Constant, Function, Variable
from rewrite import RewriteRule, RewriteSystem, normal
from xor import xor
from theories.nat import Nat

C = Function("C", 1, domain_sort=Nat.sort)
P = Function("P", 1, domain_sort=Nat.sort)
f = Function("f", 1)
IV = Constant("IV")
n = Variable("n", sort=Nat.sort)

r0 = RewriteRule(C(Nat.zero), IV)
rn = RewriteRule(C(Nat.S(n)), f(xor(P(Nat.S(n)), C(n))))
moo_system = RewriteSystem({r0, rn})
print("Cipher Block Chaining:", moo_system)

three = Nat.from_int(3)
print("Simplified form of the 3rd ciphertext:", normal(C(three), moo_system))
