from symcollab.algebra import Constant, Variable, Function
from symcollab.Unification.xor_rooted_unif import *



c = Constant("c")
x1 = Variable("x1")
x2 = Variable("x2")
x3 = Variable("x3")
f = Function("f", 1)

#Example 1: output feedback mode: [c, x1, f(c) + x1, x2, f(f(c)) + x2, x3, ......]

# A list of terms from which we are trying to find a subset S s.t. the xor of terms
# in S is 0.
terms1 = [c, xor(f(c), x1), xor(f(f(c)), x2)]

# Each variable x is associated with a list L of terms. x can be the xor of any subset
# of terms in L.
# For block-wise schedule, L is the set of terms that appear before x, with all the
# variables being removed.
dict1 = {x1: [c], x2: [c, xor(f(c), x1)]}

print("The first example: ")
p1 = XOR_rooted_security(terms1, dict1)
result = p1.solve()
if(result == None):
    print("No attack.")
else:
    for res in result:
        print(res)

print("\n\n\n\n")

#A contrived example: [c, x1, f(x1 + c) + x1, x2, f(f(x1 + c) + x2), x3, ......]
terms2 = [c, xor(f(xor(c, x1)), x1), f(xor(f(xor(c, x1)), x2))]
dict2 = {x1: [c], x2: [c, xor(f(xor(c, x1)), x1)]}

print("The second example: ")
p2 = XOR_rooted_security(terms2, dict2)
result = p2.solve()
if(result == None):
    print("No attack.")
else:
    for res in result:
        print(res)
