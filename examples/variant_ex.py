#!/usr/bin/env python3
import sys
sys.path.append("..")

from algebra import *
from rewrite import *

f = Function("f", 2)
x = Variable("x")
a = Constant("a")
b = Constant("b")

r = RewriteRule(f(x, x), x)

vs = VariantsFromRule(f(a, f(b, b)), r)
for v in vs:
    print(v)

r2 = RewriteRule(f(a, x), b)

vt = Variants(f(a, f(b, b)), {r, r2})
for v in vt:
    print(v)

print("Is Finite: ", is_finite(vt, -1))

print("Rewrite rule from", f(a, f(b, b)), "to", b, narrow(f(a, f(b, b)), b, {r, r2}, -1))