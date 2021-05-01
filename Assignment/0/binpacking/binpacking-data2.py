# number of items  
nitems= 15
# list of items
items = range(nitems)

# number of bins  
nbins= 15
# list of bins
bins = range(nbins)

# list of conflicts
conflicts = [(0,1), (0,4), (0,5), (0,7), (0,9), (0,11), (2,1), (2,3), (2,5), 
            (2,7), (2,9), (2,11), (4,1), (4,3), (4,5), (4,7), (4,9), (4,11),  
            (6,1), (6,4), (6,5), (6,7), (6,10), (6,11), (8,1), (8,3), (8,5), 
            (8,7), (8,9), (8,11), (10,1), (10,1), (10,3), (10,5), (10,7), 
            (10,9), (10,11)]

# maximum capacity
capacity = 20

# weights per item  
weight = {} 
weight[0] = 16
weight[1] = 4
weight[2] = 16
weight[3] = 4
weight[4] = 16
weight[5] = 4
weight[6] = 16
weight[7] = 4
weight[8] = 16
weight[9] = 4
weight[10] = 4
weight[11] = 16
weight[12] = 5
weight[13] = 7
weight[14] = 8

import binpacking
binpacking.solve(items, bins, conflicts, capacity, weight)

