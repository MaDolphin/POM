#!/usr/bin/env python3

from gurobipy import *

# item sizes a, item profits p, capacity b
def solve(a, p, b):
    model = Model("knapsack_longest")

    n = len(a)

    V = []
    E = []
    s = (0,0)
    t = (b,n)

    for i in range(1, n + 1):
        for c in range(0, b + 1 - a[i - 1]):
            E.append(((c, i - 1), (c + a[i - 1], i), p[i - 1]))
            V.append((c, i - 1))
            V.append((c + a[i - 1], i))

    for i in range(1, n + 1):
        for c in range(0, b + 1):
            E.append(((c, i - 1), (c, i), 0))
            V.append((c, i - 1))
            V.append((c, i))

    for i in range(0, n + 1):
        for c in range(0, b):
            E.append(((c, i), (c + 1, i), 0))
            V.append((c, i))
            V.append((c + 1, i))

    V = list(set(V))

    # a binary variable per item (selected or not); gives profit if selected
    x = {}
    for (i, j, _) in E:
        x[i, j] = model.addVar(name="x_%s_%s" % (i, j), vtype=GRB.BINARY)

    model.setObjective(
        quicksum(w * x[i, j] for (i, j, w) in E), GRB.MAXIMIZE
    )

    # capacity constraint
    model.addConstr(quicksum(x[i, j] for (i, j, _) in E if i == s) -
                    quicksum(x[j, i] for (j, i, _) in E if i == s) == 1)

    model.addConstr(quicksum(x[i, j] for (i, j, _) in E if i == t) -
                    quicksum(x[j, i] for (j, i, _) in E if i == t) == -1)

    for v in V:
        if v != s and v != t:
            model.addConstr(quicksum(x[i, j] for (i, j, _) in E if i == v) -
                            quicksum(x[j, i] for (j, i, _) in E if i == v) == 0)

    model.update()
    model.optimize()