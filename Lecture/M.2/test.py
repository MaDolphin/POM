#!/usr/bin/env python3
from gurobipy import *
# item sizes
a = [7, 4, 6, 4, 5, 4, 3, 4, 6, 7]

# profits
p = [5, 4, 4, 6, 4, 7, 4, 5, 7, 3]

# knapsack capacity
b = 20

E = []
n = len(a)

for i in range(1,n+1):
    for c in range(0,b-a[i-1]):
        E.append(((c,i-1),(c+a[i-1],i),p[i-1]))

for i in range(1,n+1):
    for c in range(0,b):
        E.append(((c,i-1),(c,i),0))

for i in range(0,n+1):
    for c in range(0,b-1):
        E.append(((c,i),(c+1,i),0))
