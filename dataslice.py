'''
Created on Apr 29, 2020

@author: thaih
'''
A = list(range(1,10,1)) # start,stop,step
B = list(range(9))

print("This is List A:",A)
print("This is List B:",B)

print(A[2])
print(B[6])

print("A:",A[:])

print("The first two elements of A:",A[0:2], A[:2])
print("Reading from left: ", A[3:6])
print(A[6:3:-1])
print("Reading from right: ", A[-6:-3])
print(A[-4:-7:-1])

print("Going through A in steps of 2 starting from first to last element: ", A[::2])
print("Going through A in steps of 2 starting from the last element: ",A[::-2])

S = 'This is a string.'
print(S[len(S)::-1])

colors = ['red','orange','yellow','green','blue','purple']
print(colors)
colors[5:] = ['indigo','violet']
print(colors)