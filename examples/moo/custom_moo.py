#Table 2

#Import the Libraries

from symcollab.algebra import Function, Variable

from symcollab.xor import xor

from symcollab.Unification.constrained.p_unif import p_unif

from symcollab.Unification.constrained.xor_rooted_unif import XOR_rooted_security

from symcollab.moe.custom import CustomMOO

from symcollab.moe.generator import MOOGenerator

from symcollab.moe.check import moo_check

##MOO One 

###Create the variables for the MOO Def

P = Variable("P[i]")

C1 = Variable("C[i-1]")

f =Function("f", 1)

###Create the recursive Def

t = xor(f(xor(P, f(C1))), f(C1))

###Check the def 

print("Checking", t, "...")

###Use the CustomMOO() function to create the base case

tm = CustomMOO(t)

###Run the security check

M=moo_check(tm.name, 'every', XOR_rooted_security, 3, True, True)

###Check Results

print("MOO is secure" if M.secure else "MOO is not secure")

############################################################

##MOO Two

###Create the variables for the MOO Def

P = Variable("P[i]")

C1 = Variable("C[i-1]")

f =Function("f", 1)

###Create the recursive Def

t = f(xor(xor(P, f(C1)), f(P)))

###Check the def 

print("Checking", t, "...")

###Use the CustomMOO() function to create the base case

tm = CustomMOO(t)

###Run the security check

M=moo_check(tm.name, 'every', p_unif, 3, True, True)

###Check Results

print("MOO is secure" if M.secure else "MOO is not secure")

############################################################

##MOO Three

###Create the variables for the MOO Def

P = Variable("P[i]")

C1 = Variable("C[i-1]")

f =Function("f", 1)

###Create the recursive Def

t = xor(f(xor(f(P), C1)),f(xor(f(P), f(C1))))

###Check the def 

print("Checking", t, "...")

###Use the CustomMOO() function to create the base case

tm = CustomMOO(t)

###Run the security check

M=moo_check(tm.name, 'every', XOR_rooted_security, 3, True, True)

###Check Results

print("MOO is secure" if M.secure else "MOO is not secure")


