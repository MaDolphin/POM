from gurobipy import *


def solve(a, p, b):
    nitems = len(p)
    items = range(nitems)

    # Do not change the following line!
    vertices = [(c, i) for i in range(nitems+1) for c in range(b+2)]
    # TODO: Generate arcs ----------------------------------------
    arcs = []  # Use whatever format suits your needs
    #itemarcs:
    for i in range(1, nitems+1):
        for c in range(b-a[i-1]+2):
            arc = [(c ,i-1), (c+a[i-1]+1, i), p[i-1]]
            arcs.append(arc)
    #skip arcs
    for i in range(1,nitems+1):
        for c in range(b+2):
            arc = [(c, i-1), (c, i), 0]
            arcs.append(arc)
    #waste arcs
    for i in range(nitems+1):
        for c in range(b+1):
            arc = [(c, i), (c+1, i), 0]
            arcs.append(arc)

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
        # x["TODO"] = model.addVar(name="x_(%s,%s),(%s,%s)" % "TODO")
        x[(arc[0],arc[1])] = model.addVar(
            vtype='b', 
            name="x_(%s,%s),(%s,%s)" % (arc[0][0],arc[0][1],arc[1][0],arc[1][1]), 
            obj= arc[2]
            )
    # -------------------------------------------------------------------------

    # Update the model to make variables known.
    # From now on, no variables should be added.
    model.update()

    # TODO: Add your constraints ----------------------------------------------
    # flow conservation constraints    
    s = (0,0)
    t = (b+1,nitems)

    for (c,i) in vertices:
        # right hand side
            rhs = 0
            if (c ,i) == s:
                rhs = 1
            if (c, i) == t:
                rhs = -1
# now the flow balancei
            model.addConstr(
                # outgoing edges
                quicksum([x[(arc[0],arc[1])] for arc in arcs if arc[0] == (c, i)]) -
                # incoming edges
                quicksum([x[(arc[0], arc[1])] for arc in arcs if arc[1] == (c, i)])
                == rhs, name="flow_"+str(i)+str(c)
                )
    #add foum for packed item
    # for i in range(1, nitems+1):
    #     for c in range(b-a[i-1]+1):
    #         if c+a[i-1]+1 < b: 
    #             model.addConstr(x[((c ,i-1), (c+a[i-1],i))] == x[((c+a[i-1],i), (c+a[i-1]+1,i))])
    # -------------------------------------------------------------------------

    model.update()
    # For debugging: print your model
    model.write('model.lp')
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
                if x[(arc[0], arc[1])].x == 1:
                    print(arc)
        else:
            print("No solution!")
    # -------------------------------------------------------------------------

    printSolution()
    # Please do not delete the following line
    return model
