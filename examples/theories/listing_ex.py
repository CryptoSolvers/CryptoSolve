from theories.listing import Listing
from theories.nat import Nat

# Empty list is of length 0
result = Listing.simplify(
    Listing.length(Listing.nil)
)
print("length(nil) is", result, flush=True)
assert result == Nat.zero

# Tail of three element is
result = Listing.simplify(
    Listing.cons(Nat.zero, Listing.cons(Nat.zero, Listing.cons(Nat.zero, Listing.nil)))
)
print("tail([0, 0, 0]) is", result, flush=True)
assert result == Listing.cons(Nat.zero, Listing.cons(Nat.zero, Listing.nil))
