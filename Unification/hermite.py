#Hermite Normal Form
#Refernce: Cohen, "A Course in Computational Algebraic Number Theory".
#Springer, GTM 138. Page 68.

#!/usr/bin/env python3
from algebra import *
import numpy as np
import math
from sympy.solvers.diophantine import diophantine
from sympy import symbols
from sympy.matrices import *
from sympy.solvers.diophantine import diop_linear
from sympy.parsing.sympy_parser import parse_expr
from collections import Counter



def hermite(A, m: int, n: int):

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
		
			
	 
	
	
	
	
