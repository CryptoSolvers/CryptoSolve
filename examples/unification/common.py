from collections import Counter
from typing import Set

from symcollab.algebra import Equation, SubstituteTerm, get_vars, unravel
from symcollab.Unification.equiv import syntactic_equal

def check_domain(problem: Set[Equation], unifier: SubstituteTerm):
    """
    Checks to see if the domain of the unifier captures all the
    variables within the problem.

    NOTE: Not necessarily indicative of an incorrect unifier.
    """
    for eqs in problem:
        left_vars = get_vars(eqs.left_side, True)
        right_vars = get_vars(eqs.right_side, True)
        original_variables = left_vars.union(right_vars)
        unifier_domain = set(unifier.domain())

        if len(original_variables - unifier_domain) > 0:
            return False

    return True


def check_simple_ac_unifier(problem: Set[Equation], unifier: SubstituteTerm):
    """
    Returns whether a unifier is a solution to a set of equations.
    Assumes that there's only one function symbol that's AC
    and no constants.
    """
    for eqs in problem:
        left_vars = get_vars(eqs.left_side)
        right_vars = get_vars(eqs.right_side)

        # Count instances of variables on the left
        # side after substitution is applied
        left_substituted_solution = Counter()
        for l in left_vars:
            l_sub = unravel(l, unifier)
            l_sub_vars = get_vars(l_sub)
            for lsv in l_sub_vars:
                left_substituted_solution[lsv] += 1

        # Count instances of variables on the right
        # side after substitution is applied
        right_substituted_solution = Counter()
        for r in right_vars:
            r_sub = unravel(r, unifier)
            r_sub_vars = get_vars(r_sub)
            for rsv in r_sub_vars:
                right_substituted_solution[rsv] += 1

        # Inequal amount of variables on each side indicate
        # an incorrect unifier
        if left_substituted_solution != right_substituted_solution:
            return False

    return True

def print_failures(problem: Set[Equation], sol: Set[SubstituteTerm], check_unifier):
    """
    Print the number of unifiers that do not
    solve the problem and try to indicate the failure type.
    """
    num_domain_failures = 0
    num_substitution_failures = 0
    num_failures = 0
    for s in sol:
        if not check_unifier(problem, s):
            num_failures += 1
            if not check_domain(problem, s):
                num_domain_failures += 1
            else:
                num_substitution_failures += 1

    print("Domain Failures:", num_domain_failures)
    print("Substitution Failures:", num_substitution_failures)
    print("Total Failures:", num_failures)

def print_sol(sol: Set[SubstituteTerm], print_num: int = 5):
    if len(sol) == 0:
        print("No Solution\n")
        return

    print_num = min(len(sol), print_num)
    print(f"First {print_num} solutions")
    sol_iter = iter(sol)
    for i in range(print_num):
        print("Solution", i, next(sol_iter))

    print("Total Solutions:", len(sol))

def print_unique_sol(sol: Set[SubstituteTerm], print_num: int = 3):
    if len(sol) == 0:
        print("No Solution\n")
        return
    print("Total Solutions:", len(sol))

    # Compute "unique" solutions
    sol_iter = iter(sol)
    unique_sols = {next(sol_iter)}
    for s in sol_iter:
        if all((not syntactic_equal(s, us) for us in unique_sols)):
            unique_sols.add(s)
    print("Unique Solutions:", len(unique_sols))

    print_num = min(len(unique_sols), print_num)
    print(f"First {print_num} unique solutions")
    sol_iter = iter(unique_sols)
    for i in range(print_num):
        print("Solution", i, next(sol_iter))