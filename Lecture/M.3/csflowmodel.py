from gurobipy import *

def solve(m, L, demands, lengths):
    # The number of orders
    n = len(demands)
    orders = range(n)

    model = Model('Сutting stock Flow')
    model.modelSense = GRB.MINIMIZE

    vertices = [i for i in range(-1, L + 1)]
    arcs = []
    arcs_1_i = []
    arcs_2 = []
    arcs_temp = []

    for i in orders:
        for k in range(L - lengths[i] + 1):
            arc = [(k, k + lengths[i]), lengths[i]]
            arcs_1_i.append(arc)

    for k in range(L):
        arc = [(k, k + 1), 0]
        arcs_2.append(arc)

    arcs = arcs_1_i + arcs_2
    arcs.append([(-1,0),m])

    def fun_arcs_1_i(i):
        arcs_temp.clear()
        for k in range(L - lengths[i] + 1):
            arc = [(k, k + lengths[i]), lengths[i]]
            arcs_temp.append(arc)
        return arcs_temp

    x = {}
    for arc in arcs:
        x[arc[0]] = model.addVar(name="x_(%s,%s)" % (arc[0][0],arc[0][1]),
                                 vtype = GRB.INTEGER,
                                 obj = arc[1])
    # model.setObjective(
    #     x[(-1,0)], GRB.MINIMIZE
    # )

    for i in orders:
        model.addConstr(quicksum(x[arc[0]] for arc in fun_arcs_1_i(i)) >= demands[i])

    for v in vertices:
        if v != -1 and v != L:
            model.addConstr(quicksum(x[(i,j)] for (i,j) in arcs if i == v) -
                            quicksum(x[(j,i)] for (j,i) in arcs if i == v) == 0)

    model.update()
    model.optimize()

    # Do not modify the code below this line
    return model