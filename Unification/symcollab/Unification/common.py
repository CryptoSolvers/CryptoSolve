"""
Common rules used in Unification algorithms
"""
from typing import Optional, Set, Tuple

from symcollab.algebra import (
    Constant, Equation, FuncTerm, get_vars, SubstituteTerm, Term, Variable
)

__all__ = [
    'delete_trivial',
    'function_clash',
    'occurs_check',
    'decompose',
    'orient',
    'eliminate',
    'variable_replacement',
    'remove_rule'
]

def delete_trivial(equations: Set[Equation]) -> Set[Equation]:
    """
    Delete Rule

    Removes {t = t} from the equation set.
    """
    equations_to_remove : Set[Equation] = set()
    for equation in equations:
        if equation.left_side == equation.right_side:
            equations_to_remove.add(equation)

    # Remove trivial equations
    return equations - equations_to_remove

def function_clash_condition(equation: Equation) -> bool:
    """
    Check for Function Clash

    Returns True if a function clash is found.
    f(s0,...sn) = g(t0,...,tn) => ⊥
    """
    el = equation.left_side
    er = equation.right_side
    return isinstance(el, FuncTerm) and \
           isinstance(er, FuncTerm) and \
           el.function != er.function

def function_clash(equations: Set[Equation]) -> bool:
    """
    Check for Function Clash

    Returns True if a function clash is found.
    {f(s0,...sn) = g(t0,...,tn)} => ⊥
    """
    return any((
        function_clash_condition(equation)
        for equation in equations
    ))

def occurs_check_condition(equation: Equation) -> bool:
    """
    Check for Occurance

    Returns True if Occurs Check
    if {x = f(s0,...,sn)} and x in vars(f(s0,...,sn)) => ⊥
    """
    el = equation.left_side
    er = equation.right_side
    return isinstance(el, Variable) and el in get_vars(er, unique=True)

def occurs_check(equations: Set[Equation]) -> bool:
    """
    Check for Occurance

    Returns True if Occurs Check
    if {x = f(s0,...,sn)} and x in vars(f(s0,...,sn)) => ⊥
    """
    return any((
        occurs_check_condition(equation)
        for equation in equations
    ))

def decompose(equations: Set[Equation]) -> Set[Equation]:
    """
    Applies decomposition to an equation.
    If it is not possible, it will return None.

    f(s1,...,sn)=f(t1,...,tn) -> s1=t1,...,sn=tn

    Returns None if the rule cannot be matched.
    """
    new_equations: Set[Equation] = set()
    matched_equation: Optional[Equation] = None

    # Find a match for the decomposition rule
    # and create the new equations if found.
    for equation in equations:
        el = equation.left_side
        er = equation.right_side
        if isinstance(el, FuncTerm) and \
           isinstance(er, FuncTerm) and \
           el.function == er.function:
            matched_equation = equation
            for i in range(el.function.arity):
                new_equations.add(Equation(
                    el.arguments[i],
                    er.arguments[i]
                ))
            break # Only match one equation

    # If the rule isn't matched, return the original input
    if matched_equation is None:
        return equations

    # Remove previous equation and add decomposed ones
    return (equations - {matched_equation}) | new_equations

def orient(equations: Set[Equation]) -> Set[Equation]:
    """
    Returns an orriented set of equations,
    meaning that the variable is always in the left
    side.
    """
    new_equations = set()
    for equation in equations:
        el = equation.left_side
        er = equation.right_side
        if isinstance(er, Variable) and isinstance(el, FuncTerm):
            new_equations.add(Equation(
                equation.right_side,
                equation.left_side
            ))
        else:
            new_equations.add(equation)
    return new_equations

def eliminate(
    equations: Set[Equation],
    sigma: SubstituteTerm
    ) -> Tuple[Set[Equation], SubstituteTerm]:
    """
    Eliminate Rule

    If the variable x doesn't occur in t, then
    G∪{x=t};S ⇒ G{x↦t};S{x↦t}∪{x↦t}

    Returns original equations and sigma
    if the rule cannot be matched.
    """
    matched_equation: Optional[Equation] = None

    for equation in equations:
        if isinstance(equation.left_side, Variable) and \
           not occurs_check_condition(equation):
            matched_equation = equation
            break

    if matched_equation is None:
        return equations, sigma

    # Create the new substitution
    new_sub = SubstituteTerm()
    new_sub.add(matched_equation.left_side, matched_equation.right_side)

    # Apply the new substitution to the set of equations
    new_equations = set()
    for equation in equations - {matched_equation}:
        new_equations.add(Equation(
            equation.left_side * new_sub,
            equation.right_side * new_sub
        ))

    # Compose the old and new substitutions
    sigma = sigma * new_sub

    return new_equations, sigma

def within_equation(t: Term, e: Equation):
    """
    Returns True if term t appears
    within either the left side or right
    side of equation e.
    """
    for e_part in [e.left_side, e.right_side]:
        # Split check based on Constant/Variable and FuncTerms
        if isinstance(e_part, (Constant, Variable)):
            if t == e_part:
                return True
        if isinstance(e_part, FuncTerm):
            if t in e_part:
                return True
    return False

def within_equations(t: Term, equations: Set[Equation]):
    """
    Returns True if term t appears
    within any of the equations provided.
    """
    return any(
        within_equation(t, e) for e in equations
    )

def variable_replacement(equations, orignal_equations):
    """
    Source; Boudet 1990
    Variable Replacement Rule

    If x and y appear in P and either
    y occurs in the original problem or
    x does not occur in the original problem then

    P∪{x=y} => P{x -> y}∪{x=y}

    Returns original equations and sigma
    if the rule cannot be matched.
    """
    matched_equation: Optional[Equation] = None

    for equation in equations:
        lhs = equation.left_side
        rhs = equation.right_side

        # Make sure both sides are variables
        if not isinstance(lhs, Variable) or not isinstance(rhs, Variable):
            continue

        # Original problem check:
        # Either y occurs in the OG problem or x does not occur in the OG problem
        og_problem_check = \
            within_equations(rhs, orignal_equations) or not within_equations(lhs, orignal_equations)

        if not og_problem_check:
            continue

        # Make sure that both the left hand side
        # and right hand side of the equation exist
        # in any of the other equations.
        loccurs = within_equations(lhs, equations - {equation})
        roccurs = within_equations(rhs, equations - {equation})

        # If both sides are found, we're proceeding with this equation
        # for the rest of the rule.
        if loccurs and roccurs:
            matched_equation = equation
            break

    # If no equations are found return early
    if matched_equation is None:
        return equations


    # Create the new substitution
    new_sub = SubstituteTerm()
    new_sub.add(matched_equation.left_side, matched_equation.right_side)

    # Apply the new substitution to the set of equations
    new_equations = set()
    for equation in equations - {matched_equation}:
        new_equations.add(Equation(
            equation.left_side * new_sub,
            equation.right_side * new_sub
        ))

    # Add the matched equation to the result
    new_equations.add(matched_equation)

    return new_equations


def remove_rule(equations, original_equations):
    """
    Source: Boudet 1990
    Remove rule:

    If x not in the original problem and
    x not in either s or P then
    {x=s}∪P => P

    Note: Removes useless equations
    that do not satisfy the condition 4
    of the definition of the dag solved form.
    """
    matched_equation = None
    for equation in equations:
        lhs = equation.left_side
        rhs = equation.right_side

        if not isinstance(lhs, Variable):
            continue

        # Check x \not\in V(s)
        if isinstance(rhs, (Constant, Variable)) and lhs == rhs:
            continue
        if isinstance(rhs, FuncTerm) and lhs in rhs:
            continue

        # Check x \not\in V(P^0)
        if within_equations(lhs, original_equations):
            continue

        # Check x \not\in V(P)
        if within_equation(lhs, equations - {equation}):
            continue

        matched_equation = equation
        break

    if matched_equation is None:
        return equations

    return equations - {matched_equation}
