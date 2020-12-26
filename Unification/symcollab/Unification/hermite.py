#Hermite Normal Form
#Refernce: Cohen, "A Course in Computational Algebraic Number Theory".
#Springer, GTM 138. Page 68.

#!/usr/bin/env python3
from symcollab.algebra import *
import numpy as np # type: ignore
import math
from sympy.solvers.diophantine import diophantine # type: ignore
from sympy import symbols # type: ignore
from sympy.matrices import * # type: ignore
from sympy.solvers.diophantine import diop_linear # type: ignore
from sympy.parsing.sympy_parser import parse_expr # type: ignore
from collections import Counter



def hnf1(A, m: int, n: int):

	#The Hermite normal form matrix
	W = zeros(m, n)

	#initialize
	m-=1
	n-=1
	i = m
	k = n
	if m <= n:
		l = 0
	else:
		l = m - n + 1 
	notend = 1
	while notend:
		#Step 2: Row finished?
		while ((not RowTest(A, i, k)) and A[i,k] >= 0):
			#Step 3: Choose non-zero entry
			minabs = [A[i,0], 0]
			for j in range(0, k):
				if minabs[0] > abs(A[i,j]):
					minabs[0]= abs(A[i,j])
					minabs[1]= j
			if A[i, k] < 0:
				A[:,k] = -A[:,k]
			b = A[i,k]
			if minabs[1] < k:
				temp = A[:, k]
				A[:, k] = A[:, minabs[1]]
				A[:, minabs[1]] = temp
			#Step 4: Reduce
			for j in range(0, k-1):
				q = math.floor((A[i,j]/b) + .5)
				A[:,j] = A[:,j] - q * A[:, k]
		
			

		#rest of step 2
		if A[i,k] < 0:
			A[:,k] = -A[:, k]
		#Step 5: Final Reduce
		b = A[i,k] 
		if b != 0:
			for j in range(k+1, n):
				q = math.floor(A[i,j]/b)
				A[:,j] = A[:,j] - q * A[:, k]
		else:
			k += 1
			
		#Step 6: Finished?	
		if i == l:
			#Done, finish up
			for j in range(0, (n - k+1)):
				W[:, j] = A[:, j+k-1]
			notend = 0
		else:
			i = i - 1
			k = k - 1	
		
	return W
			
	

def RowTest(A, i: int, k: int):
	test = True
	for j in range(0, k-1):
		if A[i, j] 	!= 0:
			test = False	
	return test				
		
			
	 
def hnf2(A, r: int, c: int):
	#initialize
	W = zeros(r, c)
	i = r - 1
	j = c - 1
	k = c - 1
	
	if r <= c:
		l = 1
	else:
		l = r - c + 1
	done = False
	while not done:
		if j != 1:
			j = j-1
			if A[i, j] != 0:
				g, u, v, mu, mv = egcd(A[i,k], A[i,j])
				B = mu * A[:,k] + mv * A[:,j]
				A[:,j] = (A[i,k] / g) * A[:,j] - (A[i,j]/g)*A[:,k]
				A[:,k] = B
		else:	
			#step 4
			b = A[i,k]
			if b < 0:
				A[:,k] = -A[:,k]
				b = -b
			if b == 0:
				k = k + 1
			else:
				for j in range(k+1, c):
					q = math.floor(A[i,j]/b)
					A[:,j] = A[:,j] - q*A[:,k]
			if i == l:
				done = True
			else:
				i = i - 1
				k = k - 1
				j = k
	for j in range(0, (c - k + 1)):
		W[:,j] = A[:, (j+k-1)]
	return W
	

def egcd(a: int, b: int):
	#for min
	md, mu, mv = a, 0, 1
	#initialize
	u = 1
	gcd = a
	if b == 0:
		v = 0
		return gcd, u, v
	else:
		v1 = 0
		v3 = b
	while v3 != 0:
		q = math.floor(gcd/v3)
		t3 = gcd%v3
		t1 = u - q*v1
		u = v1
		gcd = v3
		v1 = t1
		v3 = t3
		#test min
		v = (gcd - a * u) // b
		sv = v * sign(b)
		su = u * sign(a)
		x = -(abs(a)//gcd)
		y = abs(b)//gcd
		if( (sv > x and sv <= 0) and (su >= 1 and su <= y) and math.gcd(a,b) == gcd):
			mu = u
			mv = ((gcd - a * u) // b)
			md = gcd
	v = (gcd - a * u) // b
	return gcd, u, v, mu, mv    
    
def sign(x: int):
	if x == 0:
		return 0
	if x < 0:
		return -1
	else:
		return 1	  
	
