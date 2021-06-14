from gurobipy import *

def solve(nbins, weight, capacity):
  # Model
  model = Model("Binpacking")

  bins = range(nbins)
  items = range(len(weight))

  x = {}
  for i in items:
    for j in bins:
      x[i,j] = model.addVar(name="x_%s_%s" % (i,j), vtype=GRB.BINARY)

  # Decision variable y_j indicates whether Bin j is used (value = 1) or not (value = 0).
  y = {}
  for j in bins:
    y[j] = model.addVar(name="y_%s" % (j), vtype=GRB.BINARY)


  model.setObjective(
    quicksum(y[i] for i in bins), GRB.MINIMIZE
  )

  model.update()

  for j in bins:
    model.addConstr(quicksum(x[i, j] * weight[i] for i in items) <= capacity * y[j])

  for i in items:
    model.addConstr(quicksum(x[i, j] for j in bins) == 1)

  # redundant Constraints help to improve the performance of calculating
  # for j in bins:
  #   for i in items:
  #     model.addConstr(x[i,j] <= y[j])

  # Solve
  model.optimize()

  return model

