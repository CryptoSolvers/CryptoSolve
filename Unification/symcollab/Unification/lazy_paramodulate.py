
def lazy_paramodulate(equations: Set[Equation], rs: RewriteSystem) -> Set[Equation]:
    """
    Lazy Paramodulation Rule

    {s=t}=>{s_p=l,s[r]_p=t}
    where l->r is a matching rewrite rule and p
    is the position of the term it was matched.
    """
    matched_equation: Optional[Equation] = None
    s: Optional[Term] = None
    l: Optional[Term] = None
    r: Optional[Term] = None
    t: Optional[Term] = None

    # Side Matched: {-1: Not Found, 0: Left, 1: Right}
    side_matched = -1

    # Find a side of an equation and a rewrite rule that matches
    # function labels.
    for equation in equations:
        for i, et in enumerate((equation.left_side, equation.right_side)):
            if isinstance(et, FuncTerm):
                for rule in rs:
                    possible_applications = rule.apply(et)
                    if len(possible_applications) == 0:
                        continue
                    position_matched, t = next(iter(possible_applications.items()))
                    # TODO: Need "get_term_at_position" function, should be in the rewrite module
                    matched_equation = equation
                    s = get_term_at_position(et, position_matched)
                    l = rule.hypothesis
                    r = rule.conclusion
                    break

        # Stop looking for matches if one is found.
        if matched_equation is not None:
            break

    if matched_equation is None:
        return equations

    new_equations: Set[Equation] = set()

    # Add s=l
    l = matched_rule.hypothesis
    new_equations.add(Equation(s, l))

    # Add r=t
    r = matched_rule.conclusion
    new_equations.add(Equation(r, t))

    return (equations - {matched_equation}) | new_equations


def lazy_paramodulation(
    equations: Set[Equation],
    rs: RewriteSystem) -> SubstituteTerm:
    """
    An implementation of Lazy Paramodulation
    as described in Semantic Unification for Convergent
    Systems by Subrata Mitra.
    """
    sigma: SubstituteTerm = SubstituteTerm()

    # Breadth-First Search for the combination of
    # inference rules that leads to success
    possible_paths: List[Tuple[Equation, SubstituteTerm]] = [(equations, sigma)]
    equations_considered: List[Equation] = []

    while len(possible_paths) > 0:
        new_possible_paths: List[Tuple[Equation, SubstituteTerm]] = []
        for p_eqs, p_sigma in possible_paths:
            print(len(possible_paths))
            p_eqs = delete_trivial(p_eqs)
            print(p_eqs)

            # If the set of equations is empty, then we
            # have solved the problem.
            if len(p_eqs) == 0:
                return p_sigma

            new_equations, new_sigma = eliminate(p_eqs, p_sigma)
            if new_equations not in equations_considered:
                new_possible_paths.append((new_equations, new_sigma))
                equations_considered.append(new_equations)

            new_equations = decompose(p_eqs)
            if new_equations not in equations_considered:
                new_possible_paths.append((new_equations, p_sigma))
                equations_considered.append(new_equations)

            new_equations = lazy_paramodulate(p_eqs, rs)
            if new_equations not in equations_considered:
                new_possible_paths.append((new_equations, p_sigma))
                equations_considered.append(new_equations)

        possible_paths = new_possible_paths

    # No solution found
    return set()
