#!/usr/bin/env python3
from copy import deepcopy


def setpartitions(S: set):
	n = len(S)
	C = list()
	U = list()
	for i in range(n):
		C.append(1)
	sp(0, 1, C, n, U)
	return(U)
	

def sp(m: int, p: int, C: list, N: int, U: list):
	if p > N:
		#print(C)
		U.append(deepcopy(C))
	else:
		for i in range(1, m+1):
			C[p-1] = i
			sp(m, p+1, C, N, U)
		C[p-1] = m+1
		sp(m+1, p+1, C, N, U)


