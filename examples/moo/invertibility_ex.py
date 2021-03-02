
#Example of using the deducible function
from symcollab.algebra import Function, Variable, Constant
from symcollab.moe.invertibility import deducible
x = Constant("x")
f = Function("f", 2)
p = Constant("p_i")
deducible(f(x, p), {x})
deducible(f(x, p), {})


#example of using invertibility with MOO security check
from symcollab.algebra import Constant, Variable
from symcollab.moe.program import MOOProgram
from symcollab.moe.check import moo_check
from symcollab.Unification.xor_rooted_unif import XOR_rooted_security
from symcollab.Unification.p_unif import p_unif

result = moo_check('cipher_block_chaining', "every", p_unif, 2, True, True)
print(result.invert_result)


#example of using invertibility by itself, not how it's intended to be used
#but can be done for testing
from symcollab.moe.invertibility import InvertMOO
from symcollab.xor import xor
f = Function("f", 1)
x = Variable("x")

IV = Constant("IV")
C1 = xor(x, IV)

InvertMOO(C1, "x", L, IV, True)


