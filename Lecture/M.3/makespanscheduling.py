from gurobipy import *

def solve(nmachine, ntime, capacity):
  # Model
  model = Model("Makespanscheduling")

  jobs = range(len(ntime))
  machines = range(nmachine)

  x = {}
  for k in machines:
    for j in jobs:
      x[j,k] = model.addVar(name="x_%s_%s" % (j,k), vtype=GRB.BINARY)

  C_max = model.addVar(vtype=GRB.CONTINUOUS)

  model.setObjective(
    C_max, GRB.MINIMIZE
  )

  model.update()

  for j in jobs:
    model.addConstr(quicksum(x[j, k] for k in machines) == 1)

  for k in machines:
    model.addConstr(quicksum(x[j, k] * ntime[j] for j in jobs) <= C_max)

# only for bpp-400s-150
#   model.addConstr(C_max <= 70)

  model.optimize()

  return model

