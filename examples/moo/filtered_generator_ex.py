"""
Example usage of the FilteredMOOGenerator.
"""
from symcollab.moe.filtered_generator import FilteredMOOGenerator
from symcollab.moe.custom import CustomMOO
from symcollab.moe.check import moo_check
from symcollab.Unification.p_unif import p_unif

# Creates the generator
g = FilteredMOOGenerator(
    max_history=2,
    max_f_depth=3,
    requires_iv=False,
    requires_chaining=False
)

# Get 7th term
t = [next(g) for i in range(7)][-1]

print("The 7th term generated.") 
print(t)

# Register the custom MOO
tm = CustomMOO(t)

# Check the mode of operation
moo_check(tm.name, 'every', p_unif, 5)

print("We can also generate more random MOOs if we'd like")
print("The next 5 random MOO:")
for _ in range(5):
    print(next(g))
