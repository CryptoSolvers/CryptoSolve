from symcollab.theories.boolean import Boolean

# Neg is indempotent
result = Boolean.simplify(
    Boolean.neg(Boolean.neg(Boolean.trueb))
)
print("neg(neg(true)) is", result)
assert result == Boolean.trueb

