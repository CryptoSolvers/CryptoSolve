#!/usr/bin/env python3
import sys
sys.path.append("..")

from moe import *

# Setting up terms
s = Constant("s")
x = Variable("x")

print("One interaction with oracle example")
p = MOE(PropogatingCBC)
p.rcv_start(1)
print(p.rcv_block(1, x))

# Simulate 10 interactions
print("Simulating a 10 frame interaction with an oracle")
print(MOEInteraction(PropogatingCBC, 10))
