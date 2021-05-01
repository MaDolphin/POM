#!/usr/bin/env python3

from gurobipy import *

# number n of nodes, list E of weighted directed edges, from node s to node t
def solve(n, E, s, t) :
    model = Model("shortestpath")

    E = tuplelist(E)

    # a binary variable per item (selected or not); gives profit if selected
    x = {}
    for (i,j,_) in E:
        x[i,j] = model.addVar(name="x_%s_%s" % (i,j), vtype=GRB.BINARY)

    model.setObjective(
        quicksum(w*x[i,j] for (i,j,w) in E), GRB.MINIMIZE
    )

    # capacity constraint
    model.addConstr(quicksum(x[i, j] for (i,j,w) in E.select(s,'*')) -
                    quicksum(x[j, i] for (j,i,w) in E.select('*',s)) == 1)

    model.addConstr(quicksum(x[i, j] for (i,j,w) in E.select(t,'*')) -
                    quicksum(x[j, i] for (j,i,w) in E.select('*',t)) == -1)

    for i in range(n):
        if i != s and i != t:
            model.addConstr(quicksum(x[i,j] for (i,j,w) in E.select(i,'*')) -
                            quicksum(x[j,i] for (j,i,w) in E.select('*',i)) == 0)

    model.update()
    model.optimize()