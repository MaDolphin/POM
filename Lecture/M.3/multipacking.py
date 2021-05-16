from gurobipy import *

def solve(I, B, R, required, available, copies):
  # Model
  model = Model("Multi-dimensional Multi-Packing")

  bins = range(B)
  items = range(I)
  resources = range(R)

  x = {}
  for i in items:
      for j in bins:
        x[i,j] = model.addVar(name="x_%s_%s" % (i,j), vtype=GRB.BINARY)

  s = {}
  for j in bins:
      s[j] = model.addVar(name="s_%s" % (j), vtype=GRB.CONTINUOUS)

  model.setObjective(
    quicksum(s[j] for j in bins), GRB.MINIMIZE
  )

  model.update()

  for i in items:
      model.addConstr(quicksum(x[i, j] for j in bins) == copies[i])

  for r in resources:
    for j in bins:
        model.addConstr(quicksum(required[i][r] * x[i, j] for i in items) <=
                        available[j][r])

  for j in bins:
      model.addConstr(quicksum(x[i,j] for i in items) <=
                      quicksum(copies[i] for i in items)/B + s[j])

  # Solve
  model.optimize()

  return model

