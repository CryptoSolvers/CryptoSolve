from algebra import *
from collections import Counter
class Xor(Function):
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
        term = FuncTerm(self, (new_args[0], new_args[1]))
        for t in new_args[2:]:
            term = FuncTerm(self, (term, t))
        return term

xor = Xor()