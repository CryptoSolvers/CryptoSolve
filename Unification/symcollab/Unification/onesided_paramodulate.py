


def fresh_variable(equations: Set[Equation], sigma: SubstituteTerm) -> Variable:
    """
    Returns a new variable not already
    in the set of equations or substitution.
    """
    v = Variable("x'")
    in_equations = lambda x: any((
        x in get_vars(e.left_side, unique=True) or \
        x in get_vars(e.right_side, unique=True)
        for e in equations
    ))
    while v in sigma.domain() or in_equations(v):
        v = Variable(v.symbol + "'")
    return v

def imitate(
    equations: Set[Equation],
    sigma: SubstituteTerm
    ) -> Set[Equation]:
    """
    Imitate Rule
    {f(s1,...,sn)=y} ⇒ {s1=y1,...,sn=yn,y=f(y1,...,yn)}
    where y1,...,yn are new variables
    """
    matched_equation: Optional[Equation] = None

    for equation in equations:
        if isinstance(equation.left_side, FuncTerm):
            matched_equation = equation
            break

    if matched_equation is None:
        return equations

    new_equations = equations - {matched_equation}
    new_arguments = []

    # Add s1=y1,...,sn=yn
    for i in range(matched_equation.left_side.function.arity):
        si = matched_equation.left_side.arguments[i]
        yi = fresh_variable(equations, sigma)
        new_arguments.append(yi)
        new_equations.add(Equation(si, yi))

    # Add y=f(y1,...,yn)
    new_equations.add(Equation(
        matched_equation.right_side,
        matched_equation.left_side.function(*new_arguments)
    ))

    return new_equations

    
def mutate(
    equations: Set[Equation],
    rs: RewriteSystem
    ) -> Set[Equation]:
    """
    Mutate Rule

    If f(u1,...,un) → r is a rule from rs
    G∪{f(s1,...,sn)=t} ⇒ G∪{s1=u1,...,sn=un,r=t}

    If the rule cannot be matched, then None is returned.
    """
    matched_equation: Optional[Equation] = None
    matched_rule: Optional[RewriteRule] = None

    # Side Matched: {-1: Not Found, 0: Left, 1: Right}
    side_matched = -1

    # Find a side of an equation and a rewrite rule that matches
    # function labels.
    for equation in equations:
        for i, t in enumerate((equation.left_side, equation.right_side)):
            if isinstance(t, FuncTerm):
                for rule in rs:
                    if isinstance(rule.hypothesis, FuncTerm) and \
                       rule.hypothesis.function == t.function:
                        matched_equation = equation
                        matched_rule = rule
                        side_matched = i
                        break

        # Stop looking for matches if one is found.
        if matched_equation is not None:
            break

    if matched_equation is None:
        return equations

    new_equations: Set[Equation] = set()
    matched_term, t = \
        (matched_equation.left_side, matched_equation.right_side) \
        if side_matched == 0 \
        else (matched_equation.right_side, matched_equation.left_side)

    # Add s1=u1,...,sn=un
    for si, ui in zip(matched_term.arguments, matched_rule.hypothesis.arguments):
        new_equations.add(Equation(si, ui))

    # Add r=t
    r = matched_rule.conclusion
    new_equations.add(Equation(r, t))

    return (equations - {matched_equation}) | new_equations

def one_sided_paramodulation(
    equations: Set[Equation],
    rs: RewriteSystem) -> SubstituteTerm:
    """
    An implementation of One-Sided Paramodulation
    as described on the Wikipedia Entry for Unification
    https://en.wikipedia.org/wiki/Unification_(computer_science)#One-sided_paramodulation
    """
    sigma: SubstituteTerm = SubstituteTerm()

    # Breadth-First Search for the combination of
    # inference rules that leads to success
    possible_paths: List[Tuple[Equation, SubstituteTerm]] = [(equations, sigma)]
    equations_considered: List[Equation] = []

    while len(possible_paths) > 0:
        new_possible_paths: List[Tuple[Equation, SubstituteTerm]] = []

        for p_eqs, p_sigma in possible_paths:
            # If the set of equations is empty, then we
            # have solved the problem.
            if len(p_eqs) == 0:
                return p_sigma

            new_equations = decompose(p_eqs)
            if new_equations not in equations_considered:
                new_possible_paths.append((new_equations, p_sigma))
                equations_considered.append(new_equations)

            new_equations, new_sigma = eliminate(p_eqs, p_sigma)
            if new_equations not in equations_considered:
                new_possible_paths.append((new_equations, new_sigma))
                equations_considered.append(new_equations)

            new_equations = mutate(p_eqs, rs)
            if new_equations not in equations_considered:
                new_possible_paths.append((new_equations, new_sigma))
                equations_considered.append(new_equations)

            new_equations = imitate(p_eqs, p_sigma)
            if new_equations not in equations_considered:
                new_possible_paths.append((new_equations, p_sigma))
                equations_considered.append(new_equations)

        possible_paths = new_possible_paths

    # No solution found
    return set()


##########################
## Examples

from symcollab.algebra import Constant, Function
def one_sided_paramodulation_example():
    """Example using one-sided paramodulation."""
    f = Function("f", 2)
    x = Variable("x")
    y = Variable("y")
    a = Constant("a")
    b = Constant("b")
    rs = RewriteSystem({RewriteRule(f(x,x), x)})
    print(one_sided_paramodulation({
        Equation(
            f(f(x, x), y),
            f(a, b)
        )}, rs))
