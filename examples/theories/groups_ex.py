#!/usr/bin/env python3
from algebra import Constant, Function, Sort, Variable
from theories.groups import Group

int_sort = Sort("int")

zero = Constant("0", sort=int_sort)
add = Function("add", 2, domain_sort=int_sort, range_sort=int_sort)
neg = Function("neg", 1, domain_sort=int_sort, range_sort=int_sort)
g = Group(add, neg, zero, int_sort)

a = Variable("a", sort=int_sort)
b = Variable("b", sort=int_sort)

print("add(a, a) =", str(add(a, a)))
print("add(a, 0) =", str(g.simplify(add(a, zero))))
print("add(0, a) =", str(g.simplify(add(zero, a))))
print("add(a, b) =", str(add(a, b)))
print("neg(neg(a)) =", str(g.simplify(neg(neg(a)))))
