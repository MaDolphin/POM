\ Model cutting stock RMP
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  lambda_0 + lambda_1 + lambda_2
Subject To
 demand_0: lambda_0 >= 2
 demand_1: 3 lambda_1 >= 5
 demand_2: 2 lambda_2 >= 3
Bounds
End
