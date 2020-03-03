from xor import *
from algebra import *
import unittest

class TestXor(unittest.TestCase):
    def test(self):
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")
        x = Variable("x")
        y = Variable("y")
        z = Variable("z")
        self.assertEqual(xor(a, b, x, x, y, a, c), xor(xor(b, y), c))