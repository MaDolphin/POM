from gurobipy import *
import csv
import math
import re
import pandas as pd

fileName = "data1.csv"

def data_load(fileName):
    dataFrame = []
    df_temp = pd.DataFrame

    with open(fileName, "r") as file:
        for line in file:
            if re.match("#",line) != None:
                if df_temp.empty == False:
                    dataFrame.append(df_temp)
                    # print(df_temp)
                    del df_temp
                str = line.split(": ")[1].replace(',\n', '')
                df_temp = pd.DataFrame(columns = str.split(", "))
            else:
                line = line.replace(',\n', '')
                val = line.split(", ")
                df_temp_length = len(df_temp)
                df_temp.loc[df_temp_length] = val
        dataFrame.append(df_temp)

    for i in range(len(dataFrame)):
        dataFrame[i] = dataFrame[i].set_index('loc_id', drop=False)
        # print(dataFrame[i])

    df_hospitals = dataFrame[0]
    df_existing_hospitals = dataFrame[1]
    df_cities = dataFrame[2]
    df_cities_minimum = dataFrame[3]

    return df_hospitals, df_existing_hospitals, df_cities, df_cities_minimum

def euclidean_distance(x1,y1,x2,y2):
    return math.sqrt((int(x1) - int(x2))**2 + (int(y1) - int(y2))**2)

# def check_distance(hospitals, cities):
#     res = [(hos_id, cit_id)]
#     if dist > 30:
#         continue
#     return [x_i_j]


def solve(full_path_instance):
    df_hospitals, df_existing_hospitals, df_cities, df_cities_minimum = data_load(full_path_instance)

    df_hospitals_cost = df_hospitals[['costk1', 'costk2', 'costk3']]
    df_hospitals_cap = df_hospitals[['capk1', 'capk2', 'capk3']]

    hospitals = df_hospitals.index.to_list() # J
    cities = df_cities.index.to_list() # I
    existing_hospitals = df_existing_hospitals.index.to_list() # J_2
    cities_minimum = df_cities_minimum.index.to_list() # I_2
    types_hospitals = range(3)

    ############################################################################################
    model = Model("Hospitalnetwork")
    model.modelSense = GRB.MINIMIZE

    # whether hospital j for city i is used (value = 1) or not (value = 0).
    x = {}
    for j in hospitals:
        for i in cities:
            x[j, i] = model.addVar(name="x_%s_%s" % (j, i), vtype=GRB.BINARY)

    # which type k of hospital j in {1,2,3} is used (value = 1) or not (value = 0).
    y = {}
    for j in hospitals:
        for k in range(3):
            y[j, k] = model.addVar(name="t_%s_%s" % (j, k), vtype=GRB.BINARY)

    ############################################################################################

    for i in cities:
        model.addConstr(quicksum(x[j,i] for j in hospitals) == 1)

    for j in hospitals:
        for i in cities:
            model.addConstr(x[j,i] <= quicksum(y[j,k] for k in types_hospitals))

    for j in hospitals:
        model.addConstr(quicksum(y[j,k] for k in types_hospitals) <= 1)

    for j in hospitals:
        for i in cities:
            model.addConstr(euclidean_distance(df_hospitals.loc[j]['x_coord'], df_hospitals.loc[j]['y_coord'],
                                               df_cities.loc[i]['x_coord'], df_cities.loc[i]['y_coord']) *
                            x[j,i] * y[j,0] <= 20)
            model.addConstr(euclidean_distance(df_hospitals.loc[j]['x_coord'], df_hospitals.loc[j]['y_coord'],
                                               df_cities.loc[i]['x_coord'], df_cities.loc[i]['y_coord']) *
                            x[j,i] * y[j,1] <= 20)
            model.addConstr(euclidean_distance(df_hospitals.loc[j]['x_coord'], df_hospitals.loc[j]['y_coord'],
                                               df_cities.loc[i]['x_coord'], df_cities.loc[i]['y_coord']) *
                            x[j,i] * y[j,2] <= 30)

    for i in cities_minimum:
        model.addConstr(quicksum(x[j,i] * quicksum(y[j,k] for k in [1,2]) for j in hospitals) == 1)

    for j in hospitals:
        for k in types_hospitals:
            model.addConstr(quicksum(x[j,i] * y[j,k] for i in cities) <= int(df_hospitals_cap.loc[j][k]))

    model.setObjective(quicksum(x[j,i] * y[j,k] * int(df_hospitals_cost.loc[j][k]) for i in cities for j in hospitals for k in types_hospitals) +
                    quicksum( - (1 - quicksum(y[j,k] for k in types_hospitals)) * int(df_existing_hospitals.loc[j]['closing_income']) for j in existing_hospitals))
    
    # model.setObjective(
    # quicksum(
    #     x[j,i] * y[j,k] * int(df_hospitals_cost.loc[j][k]) 
    #     for j in hospitals
    #     for i in cities
    #     for k in types_hospitals
    #     )
    # -
    # quicksum( 
    #     ( 
    #         quicksum( (1 - y[j,k]) for k in types_hospitals)) * df_existing_hospitals.loc[j]['closing_income']  
    #         for j in existing_hospitals )
    # )
    
    ############################################################################################
    model.update()
    model.optimize()

    return model

solve(fileName)