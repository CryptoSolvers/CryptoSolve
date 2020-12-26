from symcollab.theories.nat import Nat

one = Nat.S(Nat.zero)
four = Nat.S(Nat.S(Nat.S(Nat.S(Nat.zero))))

print("Four is", Nat.from_int(4))
assert Nat.from_int(4) == four

print("S(0) is", Nat.to_int(one))
assert Nat.to_int(one) == 1

print("dec(S(0)) is", Nat.simplify(Nat.dec(one)))
assert Nat.simplify(Nat.dec(one)) == Nat.zero

three = Nat.from_int(3)
two = Nat.from_int(2)
result = Nat.simplify(Nat.mult(three, two))
print("mul(S(S(S(0))), S(S(0))) is", result)
assert result == Nat.from_int(6)
