# number of items  
nitems= 10
# list of items
items = range(nitems)

# number of bins  
nbins = 10
# list of bins
bins = range(nbins)

# list of conflicts
conflicts = [(4,2), (0,8), (1,6), (2,6), (3,6), (5,6),  (1,0), (2,0), (3,0), 
             (8,7), (5,7), (1,7), (2,7), (3,7), (5,7), (0,9), (1,9), (2,9), 
             (3,9), (4,9), (5,9), (6,9), (7,9), (8,9)]

# maximum capacity
capacity = 18

# weights per item  
weight = {} 
weight[0] = 12
weight[1] = 5
weight[2] = 3
weight[3] = 6
weight[4] = 17
weight[5] = 6
weight[6] = 14
weight[7] = 11
weight[8] = 8
weight[9] = 9

import binpacking
binpacking.solve(items, bins, conflicts, capacity, weight)

