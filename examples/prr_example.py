#!/usr/bin/env python3
import sys
sys.path.append("..")

from prr import *

# Setting up terms
r = Constant("r")
s = Constant("s")
x = Variable("x")

print("One interaction with oracle example")
p = PRR(1, r, CipherBlockChaining)
print(p.send(x))

# Simulate 10 interactions
print("Simulating a 10 frame interaction with an oracle")
print(PRRInteraction(2, s, CipherBlockChaining, 10))
