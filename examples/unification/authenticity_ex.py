from symcollab.algebra import Constant, Variable, Function
from symcollab.Unification.constrained.authenticity import *


e = Function("e", 2)
d = Function("d", 2)
n = Function("n", 1)
C1 = IndexedVariable("C1")
C2 = IndexedVariable("C2")
T = IndexedVariable("T")


def check1():
    tag = e(C1, C2)
    check_security(tag)

def check2():
    tag = e(T, xor(T, C1))
    check_security(tag)

def check3():
    tag = e(n(T), xor(e(T, C1), e(T, C2)))
    check_security(tag)

def check4():
    tag = e(n(n(T)), xor(C1, d(T, C2)))
    check_security(tag)

def check5():
    tag = e(n(n(T)), xor(C1, C2))
    check_security(tag)

check1()
check2()
check3()
check4()
check5()
