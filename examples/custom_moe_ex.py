
from moe import *

#Write a string to represent your custom MOE
#Symbols currently allowed are:
#   f()
#   xor()
#   P[i]
#   C[i]
#   C[i-1]
#   IV
#   P[0]
s = "f(xor(P[i],C[i-1]))"


#Pass into solver
MOE(chaining = CustomMOE, moe_string = s)

