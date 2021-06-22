from gurobipy import *
import networkx as nx
import math
import re
import pandas as pd

def data_load(fileName):
    listSet = []
    list_temp = []
    start_flag = False
    with open(fileName, "r") as file:
        for line in file:
            if line.find('Days') > -1:
                days = int(line.split(":")[1])
            if line.find('Periods_per_day') > -1:
                periods = int(line.split(":")[1])
            if line.strip() == "":
                if list_temp:
                    listSet.append(list_temp.copy())
                    # print(list_temp)
                    list_temp.clear()
                start_flag = True;
                continue
            if start_flag == True:
                if line.find(":") > -1:
                    continue
                else:
                    list_temp.append(line.split())

    df_courses = pd.DataFrame(listSet[0], columns=['courseID','teacher','countOfLectures','minWorkingDays','countOfStudents'])
    df_courses = df_courses.set_index('courseID', drop=True)
    df_rooms = pd.DataFrame(listSet[1], columns=['roomID', 'capacity'])
    df_rooms = df_rooms.set_index('roomID', drop=True)
    dict_curricula = {}
    df_unavailability_constraints = pd.DataFrame(listSet[3], columns=['courseID','day','dayPeriod'])
    df_unavailability_constraints = df_unavailability_constraints.set_index('courseID', drop=True)

    dict_temp = {}
    for item in listSet[2]:
        for i in range(len(item)):
            if i == 1:
                dict_temp['count'] = item[i]
            if i == 2:
                dict_temp['members'] = item[i:]
        dict_curricula[item[0]] = dict_temp.copy()
        dict_temp.clear()

    return df_courses, df_rooms, dict_curricula, df_unavailability_constraints, days, periods


def solve(full_path_instance):
    df_courses, df_rooms, dict_curricula, df_unavailability_constraints, days, periods = data_load(full_path_instance)
    print(days)
    print(periods)



    model = Model("Timetables")

    ############################################################################################
    # model.update()
    # # model.write('Timetables.lp')
    # model.optimize()
    #
    # # Printing solution and objective value
    # def printSolution():
    #     if model.status == GRB.OPTIMAL:
    #         print('\n objective: %g\n' % model.ObjVal)
    #         print("Selected following matching:")
    #         for j in hospitals:
    #             for i in cities:
    #                 # add constraints
    #                 if (j,i) in id_pairs:
    #                     for k in types_hospitals:
    #                         if x[j,i].x == 1 and y[j,k].x == 1:
    #                             print((j,i,k+1,euclidean_distance(df_hospitals.loc[j]['x_coord'], df_hospitals.loc[j]['y_coord'],
    #                                             df_cities.loc[i]['x_coord'], df_cities.loc[i]['y_coord'])))
    #     else:
    #         print("No solution!")
    #
    # printSolution()

    return model

solve('comp05.ctt')
# data_load('comp02.ctt')