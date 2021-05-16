from gurobipy import *

def solve(m, L, demands, lengths):
    # The number of orders
    n = len(demands)
    orders = range(n)
    rolls = range(m)

    model = Model('Сutting stock Flow')

    vertices = [i for i in range(-1, L + 1)]
    arcs = []
    arcs_1_i = []
    arcs_2 = []

    for i in orders:
        for k in range(0, L - lengths[i] + 1):
            arc = (k, k + lengths[i])
            arcs_1_i.append(arc)

    for k in range(0, L):
        arc = (k, k + 1)
        arcs_2.append(arc)

    arcs = arcs_1_i + arcs_2
    arcs.append((-1,0))

    def fun_arcs_1_i(i):
        arcs_temp = []
        for k in range(0, L - lengths[i] + 1):
            arc = (k, k + lengths[i])
            arcs_temp.append(arc)
        return arcs_temp

    x = {}
    for arc in arcs:
        x[(arc)] = model.addVar(name="x_(%s,%s)" % (arc[0],arc[1]),
                               vtype = GRB.INTEGER)
    model.setObjective(
        x[(-1,0)], GRB.MINIMIZE
    )

    for i in orders:
        model.addConstr(quicksum(x[arc] for arc in fun_arcs_1_i(i)) >= demands[i])

    for k in range(0, L):
        model.addConstr(quicksum(x[(i,j)] for (i,j) in arcs if i == k) -
                        quicksum(x[(j,i)] for (j,i) in arcs if i == k) == 0)

    model.update()
    model.optimize()

    # Do not modify the code below this line
    return model