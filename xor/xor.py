from algebra import *
from collections import Counter
class Xor(AssocFunction):
    def __init__(self):
        super(Xor, self).__init__("xor", 2)

    def __call__(self, *args, simplify = True):
        new_args = []
        if simplify:
            # Apply xor(a,a) = identity
            var_constant_counts = Counter(args)
            new_args = []
            for term, count in var_constant_counts.items():
                if count % 2 == 1:
                    new_args += [term]
        else:
            new_args = args
        # Create simplified term
        term = XorTerm(self, (new_args[0], new_args[1]))
        for t in new_args[2:]:
            term = XorTerm(self, (term, t))
        return term

xor = Xor()
class XorTerm(AssocTerm):
    def __init___(self, *args):
        super(XorTerm, self).__init__(xor, args)
    
    def __str__(self):
        result = ""
        for i, t in enumerate(self.arguments):
            if isinstance(t, XorTerm):
                result += " ⊕ ".join(map(lambda t: str(t), t.arguments))
            else:
                result += str(t)
            result += " ⊕ " if i < len(self.arguments) - 1 else ""
        return result

