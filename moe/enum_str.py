
#!/usr/bin/env python3
from copy import deepcopy

def enum_str(D: int, s: list, sig: set):
	if D <= 0:
		temp1 = map(lambda i: "f(" + str(i) + ")", sig)
		temp2 = map(lambda i, j: "xor(" + str(i) + "," + str(j) + ")", sig, sig)
		for d in temp1:
			s.append(d)
		for d in temp2:
			s.append(d)
		return(s)
	else:
		rec = enum_str(D-1, s, sig)
		patch = deepcopy(rec)
		temp1 = map(lambda i: "f(" + str(i) + ")", list(patch))
		temp2 = map(lambda i, j: "xor(" + str(i) + "," + str(j) + ")", list(patch), list(patch))
		for i in temp1:
			s.append(i)
		for j in temp2:
			s.append(j)
		return(s)
		

s= list()
sig = {"c", "p", "r"}
