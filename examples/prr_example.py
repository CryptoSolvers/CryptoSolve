#!/usr/bin/env python3
import sys
sys.path.append("..")

from prr import *

# Setting up terms
r = Constant("r")
s = Constant("s")
x = Variable("x")

print("One interaction with oracle example")
p = PRR(CipherBlockChaining)
p.rcv_start(1)
p.rcv_block(1, r)
print(p.rcv_block(1, x))

# Simulate 10 interactions
print("Simulating a 10 frame interaction with an oracle")
print(PRRInteraction(CipherBlockChaining, 10))
