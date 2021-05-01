#!/usr/bin/env python3

from gurobipy import *

# item sizes a, item profits p, capacity b
def solve(a, p, b):
    model = Model("knapsack")   

    # a binary variable per item (selected or not); gives profit if selected
    x = {}
    for i in range(len(a)):
        x[i] = model.addVar(vtype='b', obj = p[i])
    # capacity constraint
    model.addConstr(quicksum(a[i] * x[i] for i in range(len(a))) <= b)
    # optimize
    model.ModelSense = GRB.MAXIMIZE
    model.optimize()