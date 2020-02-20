#!/usr/bin/env python3
from algebra import *
f = Function("f", 2)
a = Constant("a")
x = Variable("x")
p = Parser()
p.add(f)
p.add(x)
p.add(a)
print("Parsing f(x,a) is successful?", p.parse("f(x,a)") == f(x,a))
print("Parsing f(f(x,a),f(x,a)) is successful?", p.parse("f(f(x,a),f(x,a))") == f(f(x,a), f(x,a)))
