#!/usr/bin/env python3
import sys
sys.path.append("..")

from algebra import *
from xor import *

a = Constant("a")
b = Constant("b")
c = Constant("c")
x = Variable("x")
y = Variable("y")
z = Variable("z")

print("xor(a,b,x,x,y,a,c) =", end = " ")
print(xor(a, b, x, x, y, a, c))