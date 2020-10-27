from theories.nat import Nat
from theories.lemma import Lemma

two = Nat.from_int(2)
three = Nat.from_int(3)
six = Nat.from_int(6)
seven = Nat.from_int(7)
one = Nat.from_int(1)

l = Lemma(Nat.eq(Nat.mult(three, two), Nat.minus(seven, one)))
l.auto()

assert l.proven == True
