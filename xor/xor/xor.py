from collections import Counter
from .ac import ACFunction, ACTerm
from .structure import Zero

class Xor(ACFunction):
    def __init__(self):
        super().__init__("xor", 2)

    def __call__(self, *args, simplify = True):
        term = XorTerm(self, (args[0], args[1]))
        for t in args[2:]:
            term = XorTerm(self, (term, t))
        
        # Simplify using rewrite rule xor(a,a) = identity if set
        if simplify:
            var_constant_counts = Counter(term.flatten())
            new_args = []
            for term, count in var_constant_counts.items():
                if count % 2 == 1:
                    new_args += [term]
            if len(new_args) > 1:
                term = self(*new_args, simplify = False)
            else:
                term = Zero() if len(new_args) == 0 else new_args[0]
        
        return term

xor = Xor()
class XorTerm(ACTerm):
    def __init___(self, *args):
        super().__init__(xor, args)
    
    def __str__(self):
        result = ""
        for i, t in enumerate(self.arguments):
            if isinstance(t, XorTerm):
                result += " ⊕ ".join(map(lambda t: str(t), t.arguments))
            else:
                result += str(t)
            result += " ⊕ " if i < len(self.arguments) - 1 else ""
        return result

