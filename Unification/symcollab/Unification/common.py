"""
Common rules used in Unification algorithms
"""
from typing import List, Optional, Set, Tuple

from symcollab.algebra import Equation, FuncTerm, get_vars, SubstituteTerm, Variable

__all__ = [
    'delete_trivial',
    'function_clash',
    'occurs_check',
    'decompose',
    'orient',
    'eliminate'
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
