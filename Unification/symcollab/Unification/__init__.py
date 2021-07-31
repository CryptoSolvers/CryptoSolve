from symcollab.algebra.callable_registry import CallableRegistry

# TODO: Enforce arity of two once the following signature is implemented
# Tuple[Set[Equation], Optional[Or[str, RewriteSystem]]] -> Set[SubstituteTerm]
Unification_Algorithms = CallableRegistry()
