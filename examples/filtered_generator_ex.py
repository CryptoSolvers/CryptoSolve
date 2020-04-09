from moe import *

# Creates the generator
g = FilteredMOEGenerator(max_history=2, max_f_depth=3, must_start_with_IV=False, must_have_chaining=False)

# Get 7th term
t = [next(g) for i in range(7)][-1]

print("The 7th term generated.") 
print(t)

# Wrap the MOESession Interfacer
tm = TermMOE(t)

# Pass it into the MOE solver
MOE(p_unif, tm, 'every', 5, 1)

print("Generate 5 more MOE")
for i in range(5):
    print(next(g))
