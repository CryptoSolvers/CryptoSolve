from symcollab.algebra import *
import unittest

class TestSympy(unittest.TestCase):
    def test(self):
        f = Function("f", 2)
        x = Variable("x")
        a = Constant("a")
        sterm = termToSympy(f(x, a))
        term = sympyToTerm(sterm)
        self.assertEqual(term, f(x, a))

if __name__ == "__main__":
    unittest.main()
