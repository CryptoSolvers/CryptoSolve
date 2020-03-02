from algebra import *
from Unification import *
from xor import xor
from copy import deepcopy
import types
import sys,imp

def enum_str(D, s, sig, f_depth = 2, nonce = True, chaining = True):
	"""Generates a random MOE string. D represents the depth, s is meant to be an emptt list, and sig represents the signature"""
	if D <= 0:
		#get two lists that have each character in sig mapped to each other character by index exactly one time
		(s1, s2) = _get_lists_for_map(list(sig))
		
		#all possible f()
		if nonce == True:
			fList = ["f(R)"]
		else: 
			fList = map(lambda i: "f(" + str(i) + ")", list(sig))
		
		#all possible xor() combinations
		if chaining == True:
			 xorList = map((lambda i, j: "xor(" + str(i) + "," + str(j) + ")"), s1, ["C"])
		else:
			xorList = map((lambda i, j: "xor(" + str(i) + "," + str(j) + ")"), s1, s2) 
		
		for i in fList:
			s.append(i) #add all f()
		for j in xorList:
			s.append(j) #add all xor()
		return(s)
	else:
		rec = enum_str(D-1, s, sig, f_depth, nonce, chaining)
		patch = deepcopy(rec)
		
		#get two lists that have each moe string mapped to each other moe string by index exactly one time
		(p1, p2) = _get_lists_for_map(list(patch)) 
		
		#all possible f(x())
		if f_depth > 0:
			fList = map(lambda i: "f(" + str(i) + ")", list(patch))
			f_depth = f_depth -1
		
		#all possible xor(x, y()) combinations 
		xorList = map(lambda i, j: "xor(" + str(i) + "," + str(j) + ")", p1, p2) 
		
		for i in fList:
			s.append(i) #add all f()
		for j in xorList:
			s.append(j) #add all xor()
		return(s)
		

def _get_lists_for_map(l):
	oldLen = len(l)
	newLen = int((oldLen * (oldLen + 1))/2)
	s1 = []
	s2 = []
	index1 = 0
	index2 = 0
	#create two lists to match each element with every other element with no duplicate pairs
	#for example if l = ["a", "b", "c"] then
	#s1 = ["a", "b", "c", "a", "b", "c"]
	#s2 = ["a", "b", "c", "b", "c", "a"]
	#each character is matched with each other character exactly one time
	#this makes the map function work properly as far as I can tell
	for x in range(newLen):
		s1.append(l[index1])
		s2.append(l[index2])
		index1 += 1
		index2 += 1
		if(index1 >= oldLen):
			index1 -= oldLen
			index2 += 1
		if(index2 >= oldLen):
			index2 -= oldLen
	return (s1, s2)


# Brandon: Commented super scary code

# basecase_str=""" f(xor(P[0], IV))"""
# reccase_str="""
#     return  f(xor(P[i], C[i-1]))"""

# tempcode =""" 
# def NewMOE(moe, session_id, iteration):
#     moe.assertIteration(session_id, iteration)
#     P = moe.plain_texts[session_id]
#     C = moe.cipher_texts[session_id]
#     IV = moe.IV[session_id]
#     f = Function("f", 1)
#     i = iteration - 1
#     if i == 0:
#         return"""+basecase_str+reccase_str

# moemod = imp.new_module("newmoe")
# exec(tempcode, moemod.__dict__)
# s = Constant("s")
# x = Variable("x")
# p = MOESession(moemod.NewMOE)
# p.rcv_start(1)
# print(p.rcv_block(1, x))

s= list()
sig = {"c", "p", "r"}
