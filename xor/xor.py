from algebra import *
from collections import Counter
class Xor(Function):
    def __init__(self):
        super(Xor, self).__init__("xor", 2)

    def __call__(self, *args):
        # Grab the variables and constants from the arguments list
        var_constants = []
        for term in args:
            var_constants += get_constants(term) + get_vars(term)
        # Apply xor(a,a) = unity
        var_constant_counts = Counter(var_constants)
        new_args = []
        for term, count in var_constant_counts.items():
            if count % 2 == 1:
                new_args += [term]
        # Create simplified term
        term = FuncTerm(self, (new_args[0], new_args[1]))
        for t in new_args[2:]:
            term = FuncTerm(self, (term, t))
        return term

xor = Xor()