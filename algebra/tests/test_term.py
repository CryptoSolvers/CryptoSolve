from symcollab.algebra import *
import unittest

class TestTerm(unittest.TestCase):
    def test_sorts(self):
        # Simple sort test
        reals = Sort("reals")
        non_zeros = Sort("non_zeros", reals)
        self.assertLess(non_zeros, reals)
        divide = Function("divide", 2, [reals, non_zeros], reals)
        one = Constant("1", non_zeros)
        zero = Constant("0", reals)
        with self.assertRaises(ValueError):
            divide(one, zero)

    def test_utilities(self):
        f = Function("f", 2)
        x = Variable("x")
        y = Variable("y")
        z = Variable("z")
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")
        self.assertListEqual(get_constants(f(a, b)), [a, b])
        self.assertListEqual(get_vars(f(x, y)), [x, y])
        self.assertListEqual(get_vars_or_constants(f(x, f(a, b))), [x, a, b])
        self.assertEqual(depth(f(f(x,a), f(x,a))), 2)

if __name__ == "__main__":
    unittest.main()
