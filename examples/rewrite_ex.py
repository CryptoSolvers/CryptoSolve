#!/usr/bin/env python3
from rewrite import *
from algebra import *
a = Constant("a")
b = Constant("b")
c = Constant("c")
x = Variable("x")
y = Variable("y")
f = Function("f", 2)
g = Function("g", 2)

r = RewriteRule(f(y, g(x, a)), g(y, a))

term = f(b, g(c, a))
print("Applying " + str(r) + " to " + str(term))
print("Result:", r.apply(term))

print("Now to show what happens when you can't apply a term...")
term = f(a,b)
print("Applying " + str(r) + " to " + str(term))
print("Result:", r.apply(term))

print("Applying f(x, x) -> x to f(f(x, x), f(x, x))")
term = f(f(x, x), f(x, x))
r = RewriteRule(f(x, x), x)
print("Result:", r.apply(term))

print("Applying f(x, x) -> x to f(f(x, x), f(x,x)) at position 2")
print("Result:", r.apply(term, '2'))