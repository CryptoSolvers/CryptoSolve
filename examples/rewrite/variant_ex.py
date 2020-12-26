#!/usr/bin/env python3
from symcollab.algebra import Constant, Function, Variable
from symcollab.rewrite import RewriteRule, RewriteSystem, narrow, is_finite, Variants

f = Function("f", 2)
x = Variable("x")
a = Constant("a")
b = Constant("b")

r = RewriteRule(f(x, x), x)
r2 = RewriteRule(f(a, x), b)
print("Rewrite Rule 1:", r)
print("Rewrite Rule 2:", r2)
term = f(a, f(b, b))
rs = RewriteSystem({r, r2})
vt = Variants(term, rs)
print("Variants of", term, ":", list(vt))

print("Variants Finite?", is_finite(vt, -1))

print("Rewrite rule from", term, "to", f(a, b), narrow(term, f(a,b), rs, -1))