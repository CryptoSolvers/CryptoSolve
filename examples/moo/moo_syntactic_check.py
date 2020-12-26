"""
Examples from Hai's presentation on May 23rd 2020
"""
from symcollab.algebra import Function, Variable, Constant
from symcollab.xor import xor
from symcollab.xor.structure import Zero
from symcollab.moe.syntactic_check import moo_depth_random_check, \
     moo_has_random, moo_f_depth


f = Function("f", 1)
r = Constant("r")
x = Variable("x")
x2 = Variable("x2")
zero = Zero()


print("Example 1.")
t1 = moo_f_depth(
    f(f(r))
)
print(f"f_depth(f(f(r))) = {t1}")
print("")


print("Example 2.")
t2 = moo_f_depth(
    xor(
        f(f(r)),
        f(r)
    )
)
print(f"f_depth(f(f(r)) ⊕ f(r)) = {t2}")
print("")


print("Example 3.")
possible_subs1 = dict()
possible_subs1[x] = [r, f(r)]
t3 = moo_f_depth(
    xor(f(r), x),
    possible_subs1
)
print(f"If {x} maps to {r} or {f(r)}...")
print(f"f_depth(f(r) ⊕ x) = {t3}")
print("")


print("Example 4.")
possible_subs2 = dict()
possible_subs2[x] = [r, zero]
t4 = moo_f_depth(
    xor(f(r), x),
    possible_subs2
)
print(f"If {x} maps to {r} or {zero}...")
print(f"f_depth(f(r) ⊕ x) = {t4}")
print("")


print("Example 5.")
possible_subs3 = dict()
possible_subs3[x] = [r]
possible_subs3[x2] = [r, f(zero)]
t5 = moo_f_depth(
    xor(
        f(xor(
            f(zero),
            x,
            r
        )),
        x2
    ),
    possible_subs3
)
print(f"If {x} maps to {r}")
print(f"and {x2} maps to {r} and {f(zero)}...")
print(f"f_depth(f(f(0) ⊕ x1 ⊕ r) ⊕ x2) = {t5}")
print("")


print("Example 6.")
t6 = moo_has_random(f(r))
print(f"has_randomness(f(r)) is {t6}")
print("")


print("Example 7.")
t7 = moo_has_random(xor(f(r), f(r)))
print(f"has_randomness(f(r) ⊕ f(r)) is {t7}")
print("")


print("Example 8.")
possible_subs4 = dict()
possible_subs4[x] = [r, f(r)]
t7 = moo_has_random(
    xor(f(r), x),
    possible_subs4
)
print(f"If {x} maps to {r} or {f(r)}...")
print(f"has_randomness(f(r) ⊕ x) is {t7}")
print("")


print("Example 9.")
possible_subs5 = dict()
possible_subs5[x] = [r, zero]
t9 = moo_has_random(
    xor(f(r), x),
    possible_subs5
)
print(f"If {x} maps to {r} or {zero}...")
print(f"has_randomness(f(r) ⊕ x) is {t9}")
print("")

# TODO: Add example for moo_depth_random_check
