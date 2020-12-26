from symcollab.algebra import *
import unittest

class TestSubstitute(unittest.TestCase):
    def test(self):
        f = Function("f", 2)
        g = Function("g", 2)
        x = Variable("x")
        y = Variable("y")
        z = Variable("z")
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")
        sigma = SubstituteTerm()
        sigma.add(x, g(y,c))
        sigma.add(z, b)
        self.assertEqual(f(x, z) * sigma, f(g(y, c), b))
        self.assertSetEqual(set(sigma.domain()), {x, z})
        self.assertSetEqual(set(sigma.range()), {g(y,c), b})
        sigma.remove(z)
        self.assertEqual(len(sigma), 1)
        sigma2 = SubstituteTerm()
        sigma2.add(y, a)
        # Need to surround the sigma multiplication in parenthesis
        # otherwise it won't compose and just both apply to f(x, b)
        self.assertEqual(f(x, b) * (sigma * sigma2), f(g(a, c), b))
        
if __name__ == "__main__":
    unittest.main()
