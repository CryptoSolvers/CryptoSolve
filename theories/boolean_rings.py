from algebra import *
from .ac import *
# Addition and multiplication are AC
# x + x = 0
# x * x = x

class BoolRingZero(Constant):
    def __init__(self):
        super().__init__("0")
    def __add__(self, x):
        return x
    def __mul__(self, x):
        return BoolRingZero()

class BoolRingAdd(ACFunction):
    def __init__(self):
        super().__init__("add", 2)

    def __call__(self, *args, simplify = True):
        # Remove zero elements
        args = [x for x in args if x != BoolRingZero()]
        if len(args) == 1:
            return args[0]
        elif len(args) == 0:
            return BoolRingZero()

        # Begin term
        term = BoolRingAddTerm(self, (args[0], args[1]))
        for t in args[2:]:
            term = BoolRingAddTerm(self, (term, t))
        
        # Simplify using rewrite rule add(a,a) = zero if set
        if simplify:
            var_constant_counts = Counter(term.flatten())
            new_args = []
            for term, count in var_constant_counts.items():
                if count % 2 == 1:
                    new_args += [term]
            if len(new_args) > 1:
                term = self(*new_args, simplify = False)
            else:
                term = BoolRingZero() if len(new_args) == 0 else new_args[0]
        
        return term


class BoolRingAddTerm(ACTerm):
    def __init___(self, *args):
        super().__init__(BoolRingAdd(), args)
    
    def __str__(self):
        result = ""
        for i, t in enumerate(self.arguments):
            if isinstance(t, BoolRingAddTerm):
                result += " ⊕ ".join(map(lambda t: str(t), t.arguments))
            else:
                result += str(t)
            result += " ⊕ " if i < len(self.arguments) - 1 else ""
        return result

class BoolRingMul(ACFunction):
    def __init__(self):
        super().__init__("add", 2)

    def __call__(self, *args, simplify = True):
        # Anything multiplied by zero is zero
        if BoolRingZero() in args:
            return BoolRingZero()
        
        term = BoolRingMulTerm(self, (args[0], args[1]))
        for t in args[2:]:
            term = BoolRingMulTerm(self, (term, t))
        
        # Simplify using rewrite rule mul(a,a) = a if set
        if simplify:
            new_args = list(set(term.flatten())) # Rewrite rule makes it so that only one instance of a var/constant appears
            if len(new_args) > 1:
                term = self(*new_args, simplify = False)
            else:
                term = BoolRingZero() if len(new_args) == 0 else new_args[0]
        
        return term


class BoolRingMulTerm(ACTerm):
    def __init___(self, *args):
        super().__init__(BoolRingMul(), args)
    
    def __str__(self):
        result = ""
        for i, t in enumerate(self.arguments):
            if isinstance(t, BoolRingMulTerm):
                result += " ⊗ ".join(map(lambda t: str(t), t.arguments))
            else:
                result += str(t)
            result += " ⊗ " if i < len(self.arguments) - 1 else ""
        return result


class BooleanRingElement(GenericTerm):
    def __init__(self, symbol : str):
        super().__init__(symbol)
    def __add__(self, x):
        add = BoolRingAdd()
        return add(self, x)
    def __mul__(self, x):
        mul = BoolRingMul()
        return mul(self, x)