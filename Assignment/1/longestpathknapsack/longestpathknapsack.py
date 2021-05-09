from gurobipy import *


def solve(a, p, b):
    nitems = len(p)
    items = range(nitems)

    # Do not change the following line!
    vertices = [(c, i) for i in range(nitems+1) for c in range(b+2)]
    # TODO: Generate arcs ----------------------------------------
    arcs = "TODO"  # Use whatever format suits your needs
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
        x["TODO"] = model.addVar(name="x_(%s,%s),(%s,%s)" % "TODO")
    # -------------------------------------------------------------------------

    # Update the model to make variables known.
    # From now on, no variables should be added.
    model.update()

    # TODO: Add your constraints ----------------------------------------------

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
                pass
                # if x["TODO"].x == 1:
                #     print(arc)
        else:
            print("No solution!")
    # -------------------------------------------------------------------------

    printSolution()
    # Please do not delete the following line
    return model
