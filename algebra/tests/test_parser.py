from symcollab.algebra import *
import unittest

class TestParser(unittest.TestCase):
    def test(self):
        f = Function("f", 2)
        a = Constant("a")
        b = Constant("b")
        x = Variable("x")
        p = Parser()
        p.add(f)
        p.add(x)
        p.add(a)
        p.add(b)
        p.remove(b)
        self.assertEqual(p.parse("f(x,a)"), f(x,a))
        self.assertEqual(p.parse("f(f(x,a),f(x,a))"), f(f(x,a), f(x,a)))
        self.assertEqual(p.parse("x"), x)
        with self.assertRaises(ValueError):
            p.add(Variable("a"))

if __name__ == "__main__":
    unittest.main()
