from rewrite import *
from algebra import *
import unittest

class TestRewrite(unittest.TestCase):
    def test(self):
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")
        x = Variable("x")
        y = Variable("y")
        f = Function("f", 2)
        g = Function("g", 2)

        r = RewriteRule(f(y, g(x, a)), g(y, a))

        term = f(b, g(c, a))
        self.assertEqual(r.apply(term)[''], g(b, a))

        term = f(a,b)
        self.assertEqual(r.apply(term), None)

        print("Applying f(x, x) -> x to f(f(x, x), f(x, x))")
        term = f(f(x, x), f(x, x))
        r = RewriteRule(f(x, x), x)
        self.assertEqual(r.apply(term)['1'], f(x, f(x, x)))
        self.assertEqual(r.apply(term, '2'), f(f(x,x), x))
