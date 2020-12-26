from symcollab.rewrite import *
from symcollab.algebra import *
import unittest

class TestVariant(unittest.TestCase):
    def test(self):
        f = Function("f", 2)
        x = Variable("x")
        a = Constant("a")
        b = Constant("b")

        r = RewriteRule(f(x, x), x)
        r2 = RewriteRule(f(a, x), b)
        term = f(a, f(b, b))
        rs = RewriteSystem({r, r2})
        vt = Variants(term, rs)
        self.assertTrue(is_finite(vt, -1), True)
        self.assertEqual(narrow(term, f(a,b), rs, -1)[0][1], '2')

if __name__ == "__main__":
    unittest.main()
