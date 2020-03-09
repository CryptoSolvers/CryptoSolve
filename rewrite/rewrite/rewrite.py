from algebra import *
from Unification import unif
from copy import deepcopy

@overload
def freeze(term: Variable) -> Constant:
    """"""
@overload
def freeze(term: Constant) -> Constant:
    """"""
@overload
def freeze(term: Function) -> Function:
    """"""
@overload
def freeze(term: FuncTerm) -> FuncTerm:
    """"""

def freeze(term):
    """
    Converts all the variables inside a term into constants.

    Parameters
    ----------
    term : Term
      The term in which to turn the variables into constants.
    
    Examples
    --------
    >>> from algebra import *
    >>> from rewrite import freeze
    >>> f = Function("f", 1)
    >>> x = Variable("x")
    >>> freeze(f(x))
    f(x)
    """
    term = deepcopy(term)
    if isinstance(term, Variable):
        return Constant(term.symbol)
    elif isinstance(term, FuncTerm):
        arguments = list(term.arguments)
        for i,t in enumerate(arguments):
            arguments[i] = freeze(t)
        term.set_arguments(arguments)
    return term

def _getOverlapVars(term : Term, hypothesis : Term, conclusion : Term) -> List[Variable]:
    """Return a list of variables that are overlapping with two terms hypothesis and conclusion"""
    rewrite_vars = get_vars(hypothesis, unique = True) | get_vars(conclusion, unique = True)
    term_vars = get_vars(term, unique = True)
    return list(rewrite_vars & term_vars)

def _changeVars(overlaping_vars : List[Variable], term : Term, hypothesis: Term, conclusion: Term):
    """Change variable names in hypothesis & conclusion to not overlap with overlapping_vars"""
    hypothesis = deepcopy(hypothesis)
    conclusion = deepcopy(conclusion)
    all_vars = get_vars(term, unique = True) | get_vars(hypothesis, unique = True) | get_vars(conclusion, unique = True)
    new_vars : List[Variable] = []
    # Go through all the variables that share the same symbol between the term and rewrite rule
    # and change the variables in the rewrite rule
    for v in overlaping_vars:
        new_var = v
        # Keep renaming variable in rewrite rule until it is not an already existing variable
        while new_var in all_vars:
            new_var = Variable(new_var.symbol + "_1")
        new_vars.append(new_var)
    # Create substitution between the old and new variable names and apply them
    s = SubstituteTerm()
    for old_v, new_v in zip(overlaping_vars, new_vars):
        s.add(old_v, new_v)
    return hypothesis * s, conclusion * s


## How does positions work?
# Ex: '121' means From the root term, look at the first argument, then
# the second argument of that term, and then the first argument of that term
# f(f(a, f(b, c)),d) | '121' = b
# f(a, b) | '' = f(a, b)

# New Type for better annotations
Position = str 

class RewriteRule:
    """
    Represents a single rewrite rule.
    Takes a hypothesis and a conclusion and 
    applies them to a term when given.
    """
    def __init__(self, hypothesis : Term, conclusion : Term):
        self.hypothesis = hypothesis
        self.conclusion = conclusion
    
    def apply(self, term : Term, pos : Optional[Position] = None) -> Optional[Union[Dict[Position, Term], Term]]:
        """
        Applies a rewrite rule to 
        either a position within a term 
        or all subterms.

        Parameters
        ----------
        term : Term
          The term in which to apply the RewriteRule
        pos : str, optional
          The position inside the term to rewrite. 
          If no term is given then all possible subterms are rewritten.
          See notes for details.
        
        Notes
        -----
        Positions are given as a string representing
        a sequence of indices in which to go into each subterm.
        For example, '121' indicates the first argument from the
        root term. Then, the second argument from that term, and lastly
        the third argument of that term.
        f(f(a, f(b, c)),d) | '121' = b

        Examples
        --------
        >>> from algebra import *
        >>> from rewrite import RewriteRule
        >>> f = Function("f", 1)
        >>> a = Constant("a")
        >>> b = Constant("b")
        >>> r = RewriteRule(f(a), f(b))
        >>> r.apply(f(f(a)))
        {'1': f(f(b))}
        """
        if pos is None:
            result = self._apply_all(term, '', term, dict())
            return result if len(result) != 0 else None
        return self._apply_pos(term, pos)

    
    def _match(self, term : Term) -> Optional[Term]:
        """Attempts to rewrite the root term with the rewrite rule. Returns False if not possible"""
        # Change common variables in RewriteRule if they exist
        overlaping_vars = _getOverlapVars(term, self.hypothesis, self.conclusion)
        while overlaping_vars:
            self.hypothesis, self.conclusion = _changeVars(overlaping_vars, term, self.hypothesis, self.conclusion)
            overlaping_vars = _getOverlapVars(term, self.hypothesis, self.conclusion)
        # Perform matching and substitution
        frozen_term = freeze(term)
        sigma = unif(self.hypothesis, frozen_term)
        return self.conclusion * sigma if sigma != False else None

    def _apply_pos(self, term : Term, pos : Position) -> Optional[Term]:
        term = deepcopy(term)
        if pos == '':
            return self._match(term)
        
        # Recurse down to appropriate position
        if isinstance(term, Constant) or isinstance(term, Variable):
            raise ValueError("Position " + pos + " is not valid for term " + str(term))
        index = int(pos[0])
        if index > len(term.arguments):
            raise ValueError("Position " + pos + " is not valid for term " + str(term))
        
        term.arguments = list(term.arguments)
        new_argument = self._apply_pos(term.arguments[index - 1], pos[1:])
        if new_argument is None:
            return None
        term.arguments[index - 1] = new_argument
        term.arguments = tuple(term.arguments)
        return term
    
    def _apply_all(self, term : Term, pos : Position, subterm : Term, result : Dict[Position, Term]) -> Dict[Position, Term]:
        """Applies the rewrite rule to every subterm"""     
        # If the current position is rewritable, add it to result dictionary
        r = self._apply_pos(term, pos)
        if r is not None:
            result[pos] = r
        
        # Recurse down arguments
        if isinstance(subterm, FuncTerm): 
            for i, t in enumerate(subterm.arguments):
                self._apply_all(term, pos + str(i + 1), t, result)
        
        return result
    
    def __repr__(self):
        return str(self.hypothesis) + " → " + str(self.conclusion)
    
    def __hash__(self):
        return hash((self.hypothesis, self.conclusion))
    
    def __eq__(self, other):
        return self.hypothesis == other.hypothesis and self.conclusion == other.conclusion


def converse(rule : RewriteRule) -> RewriteRule:
    """
    Returns the converse of a rewrite rule.

    This means that the hypothesis and conclusion of the rewrite rule gets flipped.

    Examples
    --------
    >>> from algebra import *
    >>> from rewrite import *
    >>> f = Function("f", 2)
    >>> a = Constant("a")
    >>> b = Constant("b")
    >>> r = RewriteRule(f(a,b), f(b,a))
    >>> converse(r)
    f(b, a) -> f(a, b)
    """
    new_rule = deepcopy(rule)
    # Flip Hypothesis and Conclusion
    temp = new_rule.hypothesis
    new_rule.hypothesis = new_rule.conclusion
    new_rule.conclusion = temp
    return new_rule


class RewriteSystem:
    """
    A set of rewrite rules. 
    Used primarily to hold properties of a rewrite system.
    """
    def __init__(self, rules : Set[RewriteRule]):
        self.rules = rules
        # self.forward_closure_complete = False
    
    def append(self, rule):
        """Add a single rule to the rewrite system"""
        self.rules.append(rule)
    
    # TODO: Does this affect the foward closure member variable?
    def extend(self, system):
        """Add a list of rules to a rewrite system"""
        self.rules.extend(system.rules)
    
    def __iter__(self):
        return iter(self.rules)
    
    # TODO: Write the machinary needed for the below method to work
    # # By Daniel Kemp
    # def forward_closure(self, bound = 1):
    #     """Run the forward closure on a rewrite system with a limit set on the number of interations. Defaults to 1 iteration"""
    #     # Don't execute again if already completed
    #     if self.forward_closure_complete:
    #         return self
        
    #     initial_rules = self.rules # R2 from the paper
    #     current_new_rules = deepcopy(self) # R1 from the paper
    #     # Start with FC0 := R, this will eventually be R3 from the paper
    #     current_fc = deepcopy(self)
        
    #     iteration = 0
    #     for iteration in range(0, bound):
    #         # Start FOV
    #         new_rules = RewriteSystem({})
    #         for rule in current_new_rules.rules:
    #             for initial_rule in initial_rules:
    #                 for position in rule.right.fpos():
    #                     overlap = rule.overlap(initial_rule, initial_rules, position)
    #                     if overlap is not False:
    #                         if not overlap.check_redundancy(initial_rules) and not overlap.check_redundancy(new_rules.rules):
    #                             new_rules.append(overlap)
    #             if len(new_rules.rules) == 0:
    #                 self.forward_closure_complete = True
    #                 self.rules = current_fc.rules
    #                 self.clean_variable_names()
    #                 return self
                
    #             print("Non-redundant rules: \n", new_rules)

    #             current_new_rules = deepcopy(new_rules)
    #             new_rules = None
    #             current_fc.extend(current_new_rules)

    #         print("Bound of {} reached but no forward closure" % (bound))
    #         self.rules = current_fc.rules
    #         self.clean_variable_names()
    #         self.forward_closure_complete = False
    #         return self

    
    def __repr__(self):
        if len(self.rules) == 0:
            return "{}"
        if len(self.rules) == 1:
            return "{ %s }" % (str(self.rules[0]))
        str_repr = "{\n"
        i = 1
        for i, rule in enumerate(self.rules):
            str_repr += "  " + str(rule)
            str_repr += ",\n" if i < len(self.rules) else ""
            i += 1
        str_repr += "\n}"
        return str_repr