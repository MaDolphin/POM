from gurobipy import *

def solve(m, L, demands, lengths):
    # The number of orders
    n = len(demands)
    orders = range(n)
    rolls = range(m)

    model = Model('Сutting stock')

    # Add the necessary attributes to the variables defined below. DO NOT RENAME these variables
    # x[i,j] depicts the number of items cut for the order i from the roll j
    x = model.addVars(n, m, vtype=GRB.INTEGER, name='x')

    # y[j] defines whether the roll j has been used
    y = model.addVars(m, vtype=GRB.BINARY, name='y', obj=1)

    for i in orders:
        model.addConstr(quicksum(x[i, j] for j in rolls) >= demands[i])

    for j in rolls:
        model.addConstr(quicksum(lengths[i] * x[i, j] for i in orders) <= L)

    for i in orders:
        for j in rolls:
            model.addConstr(x[i,j] <= demands[i]*y[j])

    model.update()
    model.optimize()

    # Do not modify the code below this line
    return model