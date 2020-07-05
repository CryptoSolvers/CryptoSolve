"""
Example for setting up a MOOProgram
"""
from algebra import Constant, Variable
from moe.moo_program import MOOProgram

# Setting up terms
s = Constant("s")
x = Variable("x")

print("One interaction with oracle example")
p = MOOProgram('propogating_cbc')
print(p.rcv_block(x))

# Stop an interaction
p.rcv_stop()
