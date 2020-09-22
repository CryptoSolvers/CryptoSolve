import theories.nat as nat

one = nat.S(nat.zero)
four = nat.S(nat.S(nat.S(nat.S(nat.zero))))

print("Four is", nat.from_int(4))
assert nat.from_int(4) == four

print("S(0) is", nat.to_int(nat.S(nat.zero)))
assert nat.to_int(one) == 1

print("dec(S(0)) is", nat.simplify(nat.dec(nat.S(nat.zero))))
assert nat.simplify(nat.dec(one)) == nat.zero

