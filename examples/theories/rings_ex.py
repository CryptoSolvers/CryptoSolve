#!/usr/bin/env python3
import sys
sys.path.append("../..")

from algebra import *
from theories import *

r = Ring("r", ACFunction("add", 2), AFunction("mul", 2), "0")
a = RingConstant(r, "a")
b = RingConstant(r, "b")
zero = r.zero

print("a + a =", str(a + a))
print("a * a =", str(a * a))
print("a + 0 =", str(a + zero))
print("a * 0 =", str(a * zero))
print("a * b = b * a is", a * b == b * a)
print("a + b = b + a is", a + b == b + a)
print("a + b =", str(a + b))
print("b * (a + a) =", str(b * (a + a)))
print("(a + a) * b =", str((a + a) * b))
print("b * (a + b) =", str(b * (a + b)))
print("a * b =", str(a * b))
print("a - a =", str(a - a))
print("a - b =", str(a - b))
print("a - 0 =", str(a - zero))
print("0 - a =", str(zero - a))