from xor.xor import xor
from xor.structure import Zero
from algebra import Function, Variable, Constant, SubstituteTerm, get_vars

class MOE_Generator:
    """Construct modes of encryption"""
    def __init__(self, max_history = 2):
        """Creates an MOE generator that only is able to look at the last two cipher or plaintext blocks"""
        self.f = Function("f", 1)
        self.r = Constant("r") # Only one nounce currently
        self.P = lambda x: Variable("P_{i-" + str(x) +"}") if x > 0 else Variable("P_{i}")
        self.C = lambda x: Variable("C_{i-" + str(x) +"}")
        self.max_history = max_history
        self.tree = [[self.f(self.P(0)), xor(self.r, self.P(0))]]
        self.branch_iter = iter(self.tree[0]) # Where we are at the branch
    
    def __iter__(self):
        return self
    
    # This function will only show for what is currently computed but it is helpful
    # for preventing repeats of the same calculations
    def __contains__(self, x):
        for branch in self.tree:
            if x in branch:
                return True
        return False
    
    def _create_next_branch(self):
        """Compute the set of random MOE terms of the next depth"""
        branch = []
        for m in self.tree[-1]:
            temp = []
            temp.append(self.f(m))
            temp.append(xor(m, self.r))
            temp.append(xor(m, self.P(0)))
            # Iterate through previous blocks
            for i in range(min(len(self.tree), self.max_history)):
                temp.append(xor(m, self.P(i + 1)))
                temp.append(xor(m, self.C(i + 1)))
            # Make sure none of the terms generated are already in the tree
            # or simplifies to just a variable of constant like
            # f(0), 0, P, C, r
            temp = filter(lambda x: 
                x not in self and \
                not isinstance(x, Variable) and \
                not isinstance(x, Constant)
            , temp)
            branch.extend(temp)
        return branch
    
    def __next__(self):
        """Returns the next random MOE term"""
        try:
            next_node = next(self.branch_iter)
        except StopIteration:
            branch = self._create_next_branch()
            if len(branch) == 0:
                raise StopIteration
            self.tree.append(branch)
            self.branch_iter = iter(self.tree[-1])
            next_node = next(self.branch_iter)
        return next_node

class TermMOE:
    """Custom MOE that works with MOE_Generator and MOESession"""
    def __init__(self, term):
        self.term = term
    def __call__(self, moe, session_id, iteration):
        moe.assertIteration(session_id, iteration)
        P = moe.plain_texts[session_id]
        C = moe.cipher_texts[session_id]
        IV = moe.IV[session_id]
        i = iteration - 1
        # Create substitution between symbolic plain and cipher texts
        # and the symbolic instantiations of them in MOESession
        sigma = SubstituteTerm()
        subterms = get_vars(self.term)
        for subterm in subterms:
            if subterm.symbol[0] == "P":
                if '-' not in subterm.symbol:
                    # Assume we mean current plaintext
                    sigma.add(subterm, P[-1])
                else:
                    j = int(subterm.symbol[4:-1])
                    if j > i:
                        # If we request for a cipher block that doesn't exist yet 
                        # due to the current session length
                        # then map the subterm to a different nounce
                        sigma.add(subterm, Constant(IV.symbol + f"_{j}"))
                    else:
                        sigma.add(subterm, P[-j])
            elif subterm.symbol[0] == "C":
                j = int(subterm.symbol[5:-1])
                if j > i:
                    # If we request for a cipher block that doesn't exist yet 
                    # due to the current session length
                    # then map the subterm to a different nounce
                    sigma.add(subterm, Constant(IV.symbol + f"_{j}"))
                else:
                    sigma.add(subterm, C[-j])
        return self.term * sigma
