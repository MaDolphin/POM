# Import the libraries
import pandas as pd
import networkx as nx
import numpy as np
import math
from gurobipy import *

# takes a graph G and a root node as input and returns a shortest path tree
def construct_spt(G, root):

    queue=[]
    queue.append(root)
    seen=[]
    seen.append(root)
    parent={root:None}

    while queue:
        vertex = queue.pop(0)
        nodes = [n for n in G.neighbors(vertex)]
        for w in nodes:
            if w not in seen:
                queue.append(w)
                seen.append(w)
                parent[w]=vertex
    
    spt = nx.create_empty_copy(G, with_data=True)

    for node in G.nodes():
        if node != root:
            shortest_path_list = []
            while node:
                shortest_path_list.append(node)
                node = parent[node]
            
            # reverse shortest_path_list
            # init list [terminal,c,b,a,root]
            # reversed list [root,a,b,c,terminal]
            reversed_shortest_path_list = list(reversed(shortest_path_list))

            # add edges
            for i in range(len(reversed_shortest_path_list)-1):
                spt.add_node(reversed_shortest_path_list[i], distance=i)
                spt.add_edge(reversed_shortest_path_list[i], reversed_shortest_path_list[i+1])
            spt.add_node(reversed_shortest_path_list[-1], distance=len(reversed_shortest_path_list)-1)

    return spt


def solve(G, req_p, pi: dict, u):
    
    # shortest-path-tree
    spt = construct_spt(G, u)

    plz_list = [m for m, _ in spt.nodes(data=True)]

    # build pricing problem
    pp = Model("political districting pricing problem")

    y={}
    for m in plz_list:
        y[m] = pp.addVar(name="y_%s" % (m), vtype=GRB.BINARY)


    # populations constrains req_p * 0.85 <= X <= req_p * 1.15
    pp.addConstr(quicksum(y[m] * spt.nodes[m]['population'] for m in plz_list) >= req_p * (1 - 0.15))
    pp.addConstr(quicksum(y[m] * spt.nodes[m]['population'] for m in plz_list) <= req_p * (1 + 0.15))

    # contiguity constrains using shortest-path-tree y0+..+ym >= ym * m
    for m in plz_list:
        path_list = nx.shortest_path(spt, source = m, target = u)
        pp.addConstr(quicksum(y[visit] for visit in path_list) >= y[m] * len(path_list))

    # solving Abs_value
    populations_deviation = pp.addVar(name="populations_deviation", vtype=GRB.INTEGER)
    pp.addConstr(populations_deviation >= quicksum(y[m] * spt.nodes[m]['population'] for m in plz_list) - req_p)
    pp.addConstr(populations_deviation >= req_p - quicksum(y[m] * spt.nodes[m]['population'] for m in plz_list))

    # pricing problem's objective
    pp.setObjective(
        quicksum(y[m] * spt.nodes[m]['distance'] for m in plz_list) + 
        populations_deviation - 
        quicksum(y[m] * pi[m] for m in plz_list) -
        pi[0], 
        GRB.MINIMIZE
    )

    # gurobi should be silent
    pp.params.outputFlag = 0

    pp.update()
    pp.optimize()
    
    return pp