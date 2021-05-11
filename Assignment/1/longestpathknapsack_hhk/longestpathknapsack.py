from gurobipy import *


def solve(a, p, b):
    nitems = len(p)
    items = range(nitems)
    s = (0, 0)
    t = (b + 1, nitems)
    a = [i + 1 for i in a]

    # Do not change the following line!
    vertices = [(c, i) for i in range(nitems+1) for c in range(b+2)]
    # TODO: Generate arcs ----------------------------------------
    arcs = []

    # item arcs ((c, i − 1),(c + a[i], i)) for i = 1, . . . , n, c = 0, . . . , b + 1 − a[i];
    # using one of these arcs represents packing item i into the knapsack
    for i in range(1, nitems + 1):
        for c in range(0, b + 2 - a[i - 1]):
            arcs.append([(c, i - 1), (c + a[i - 1], i), p[i - 1]])

    # skip arcs ((c, i − 1),(c, i)), for i = 1, . . . , n, c = 0, . . . , b + 1;
    # using one of these arcs represents not packing item i
    for i in range(1, nitems + 1):
        for c in range(0, b + 2):
            arcs.append([(c, i - 1), (c, i), 0])

    # waste arcs ((c, i),(c + 1, i)) for i = 0, . . . , n, c = 0, . . . , b + 1 − 1
    # using one of these arcs represents leaving the c’th unit of capacity
    for i in range(0, nitems + 1):
        for c in range(0, b + 1):
            arcs.append([(c, i), (c + 1, i), 0])

    # ------------------------------------------------------------------------

    # Model
    model = Model("Flowbased knapsack")
    model.modelSense = GRB.MAXIMIZE

    # Decision variable x_a indicates whether arc a is selected (value 1) or
    # not (value 0)
    # TODO: Adjust string formatting (behind the "%" sign) so that the --------
    # variables in the gurobi model will have the correct name! Also use
    # reasonable dict keys for x[...] =
    x = {}
    for arc in arcs:
        x[arc[0],arc[1]] = model.addVar(name="x_(%s,%s),(%s,%s)" % (arc[0][0],arc[0][1],arc[1][0],arc[1][1]),
                                        vtype = GRB.BINARY,
                                        obj = arc[2])
    # -------------------------------------------------------------------------

    # Update the model to make variables known.
    # From now on, no variables should be added.
    model.update()

    # TODO: Add your constraints ----------------------------------------------

    model.addConstr(quicksum(x[i, j] for [i, j, _] in arcs if i == s) -
                    quicksum(x[j, i] for [j, i, _] in arcs if i == s) == 1)

    model.addConstr(quicksum(x[i, j] for [i, j, _] in arcs if i == t) -
                    quicksum(x[j, i] for [j, i, _] in arcs if i == t) == -1)

    for v in vertices:
        if v != s and v != t:
            model.addConstr(quicksum(x[i, j] for [i, j, _] in arcs if i == v) -
                            quicksum(x[j, i] for [j, i, _] in arcs if i == v) == 0)
    # -------------------------------------------------------------------------

    model.update()
    # For debugging: print your model
    # model.write('model.lp')
    model.optimize()

    # TODO: Adjust your dict keys for x[...] to print out the selected --------
    # edges from your solution and then uncomment those lines.
    # This is not not necessary for grading but helps you confirm that your
    # model works

    # Printing solution and objective value
    def printSolution():
        if model.status == GRB.OPTIMAL:
            print('\n objective: %g\n' % model.ObjVal)
            print("Selected following arcs:")
            for arc in arcs:
                # pass
                if x[arc[0],arc[1]].x == 1:
                    print(arc)
        else:
            print("No solution!")
    # -------------------------------------------------------------------------

    printSolution()
    # Please do not delete the following line
    return model
