#!/usr/bin/env python3
import sys
sys.path.append("../..")

from algebra import *
from theories import *

g = Group("g", AFunction("f", 2))
a = GroupConstant(g, "a")
b = GroupConstant(g, "b")
identity = g.identity

print("a * a =", str(a * a))
print("a * id =", str(a * identity))
print("id * a =", str(identity * a))
print("a * b =", str(a * b))
print("b * a =", str(b * a))
print("a * b = b * a is", a * b == b * a)
print("a / a =", str(a / a))
print("a / a = a * inv(a) is", str(a / a == a * g.inv(a)))