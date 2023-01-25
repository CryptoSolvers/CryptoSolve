#!/usr/bin/env python3
from symcollab.algebra import  Variable
from symcollab.theories.groups import Group

a = Variable("a", sort=Group.sort)
b = Variable("b", sort=Group.sort)

print("add(a, a) =", str(Group.op(a, a)))
print("add(a, 0) =", str(Group.simplify(Group.op(a, Group.identity))))
print("add(0, a) =", str(Group.simplify(Group.op(Group.identity, a))))
print("add(a, b) =", str(Group.op(a, b)))
print("neg(neg(a)) =", str(Group.simplify(Group.inverse(Group.inverse(a)))))
