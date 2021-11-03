from symcollab.algebra import Constant, FuncTerm

###############################################
class Equations:
    def __init__(self, contents):
        self.contents = contents
    def __repr__(self):
        if len(self.contents) == 0:
            return " "
        return ", ".join(map(str, self.contents)) + " "

class Disequation:
    def __init__(self, lhs, rhs):
        self.left_side = lhs
        self.right_side = rhs

    def __repr__(self):
        return str(self.left_side) + " != " + str(self.right_side)

class Disequations:
    def __init__(self, contents):
        self.contents = contents
    def __repr__(self):
        if len(self.contents) == 0:
            return " no disequation "
        return ", ".join(map(str, self.contents)) + "  "



# ############################3
def Zero():
    return Constant("0")

def is_zero(term):
    return isinstance(term, Constant) and term == Zero()
###################################

#########################################
class XORTerm:
    def __init__(self, args):
        self.arguments = args
    def __repr__(self):
        return "+ ".join(map(str, self.arguments))
    # Hash needed for network library
    def __hash__(self):
        return hash(("xor", self.arguments[0]))
    def __eq__(self, x):
        return isinstance(x, XORTerm) and self.arguments == x.arguments
    def __contains__(self, term):
    #########################cannot use it
        inside = False
        for arg in self.arguments:
            if isinstance(arg, FuncTerm):
                inside = inside or (term in arg)
            else:
                inside = inside or (term == arg)
        return inside

class ConstrainedTerm:
    def __init__(self, tm, sigma):
    #term can possibly contain XOR subterms.
        self.term = tm
        self.constraint = sigma

    # Hash needed for network library
    def __hash__(self):
        return hash(("constrainedterm", self.term))

    def __eq__(self, t):
        if(not isinstance(t, ConstrainedTerm)):
            return False
        if(self.term != t.term):
            return False
        else:
            self_sub = self.constraint
            self_domain = list(self_sub.domain())
            t_sub = t.constraint
            t_domain = list(t_sub.domain())
            if(len(self_domain) != len(t_domain)):
                return False
            for var in self_domain:
                if(not (var in t_domain)):
                    return False
                elif(var * self_sub != var * t_sub):
                    return False
            return True


###################################