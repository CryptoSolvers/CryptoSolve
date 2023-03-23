from symcollab.algebra import Function, FuncTerm

__all__ = ['Xor', 'xor', 'XorTerm']

class Xor(Function):
    def __init__(self):
        super().__init__("xor", 2)

    def __call__(self, *args):
        term = XorTerm(self, (args[0], args[1]))
        for t in args[2:]:
            term = XorTerm(self, (term, t))
        return term

xor = Xor()
class XorTerm(FuncTerm):
    def __init___(self, *args):
        super().__init__(xor, args)
    
    def __str__(self):
        return " ⊕ ".join([str(ti) for ti in self.arguments])
