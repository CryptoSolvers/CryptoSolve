"""
Example usage of the MOOGenerator.
"""
from moe.generator import MOOGenerator
from moe.moo_custom import CustomMOO
from moe.moo_check import moo_check
from Unification.p_unif import p_unif


g = MOOGenerator()

# Get the 17th random term
t = [next(g) for i in range(17)][-1]

# Register the custom MOO
tm = CustomMOO(t)

# Check the mode of operation
moo_check(tm.name, 'every', p_unif, 5)

print("We can also generate more random MOEs if we'd like")
print("The next 5 random MOE:")
for _ in range(5):
    print(next(g))
