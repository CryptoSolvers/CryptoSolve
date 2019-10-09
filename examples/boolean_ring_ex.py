#!/usr/bin/env python3
import sys
sys.path.append("..")

from algebra import *
from theories import *

a = BooleanRingElement("a")
b = BooleanRingElement("b")
zero = BooleanRing.zero

print("a ⊕ a =", str(a + a))
print("a ⊗ a =", str(a * a))
print("a ⊕ 0 =", str(a + zero))
print("a ⊗ 0 =", str(a * zero))
print("a ⊗ b = b ⊗ a is", a * b == b * a)
print("a ⊕ b = b ⊕ a is", a + b == b + a)
print("a ⊕ a ⊕ b =", str(a + a + b))
print("a ⊕ b =", str(a + b))
print("a ⊗ 0 =", str(a * zero))
print("b ⊗ (a ⊕ a) =", str(b * (a + a)))
print("a ⊗ b =", str(a * b))