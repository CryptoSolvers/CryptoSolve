from moe import *

g = MOE_Generator()

# Get the 17th random term
t = [next(g) for i in range(17)][-1]

# Wrap the MOESession Interfacer
tm = TermMOE(t)

# Pass it into the MOE solver
MOE(p_unif, tm, 'every', 5, 1)

print("We can also generate more random MOEs if we'd like")
print("The next 5 random MOE:")
for i in range(5):
    print(next(g))
