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
    df_courses[['countOfLectures']] = df_courses[['countOfLectures']].astype(int)
    df_courses[['minWorkingDays']] = df_courses[['minWorkingDays']].astype(int)
    df_courses[['countOfStudents']] = df_courses[['countOfStudents']].astype(int)

    df_rooms = pd.DataFrame(listSet[1], columns=['roomID', 'capacity'])
    df_rooms = df_rooms.set_index('roomID', drop=True)
    df_rooms[['capacity']] = df_rooms[['capacity']].astype(int)

    dict_curricula = {}
    df_unavailability_constraints = pd.DataFrame(listSet[3], columns=['courseID','day','dayPeriod'])
    df_unavailability_constraints = df_unavailability_constraints.set_index('courseID', drop=True)
    df_unavailability_constraints[['day']] = df_unavailability_constraints[['day']].astype(int)
    df_unavailability_constraints[['dayPeriod']] = df_unavailability_constraints[['dayPeriod']].astype(int)

    dict_temp = {}
    for item in listSet[2]:
        for i in range(len(item)):
            if i == 1:
                dict_temp['count'] = int(item[i])
            if i == 2:
                dict_temp['members'] = item[i:]
        dict_curricula[item[0]] = dict_temp.copy()
        dict_temp.clear()

    return df_courses, df_rooms, dict_curricula, df_unavailability_constraints, days, periods


def solve(full_path_instance):
    df_courses, df_rooms, dict_curricula, df_unavailability_constraints, days, periods = data_load(full_path_instance)

    # courses K
    courses = df_courses.index.to_list()

    # rooms R
    rooms = df_rooms.index.to_list()

    # time_slots T
    time_slots = []
    for i in range(days):
        for j in range(periods):
            time_slots.append((i,j))

    # courses can be take place in which rooms K_r
    courses_rooms_pairs = {}
    set_temp = set()
    for k in courses:
        for r in rooms:
            if df_courses.loc[k]['countOfStudents'] <= df_rooms.loc[r]['capacity']:
                set_temp.add(r)
        courses_rooms_pairs[k] = set_temp.copy()
        set_temp.clear()

    # for rooms which course can be take place in R_r
    rooms_courses_pairs = {}
    set_temp.clear()
    for r in rooms:
        for k in courses:
            if df_courses.loc[k]['countOfStudents'] <= df_rooms.loc[r]['capacity']:
                set_temp.add(k)
        rooms_courses_pairs[r] = set_temp.copy()
        set_temp.clear()

    ############################################################################################

    model = Model("Timetables")
    model.modelSense = GRB.MINIMIZE

    # whether course k takes place at time-slots (i,j)
    x = {}
    for k in courses:
        for (i,j) in time_slots:
            x[k, i, j] = model.addVar(name="x_%s_(%s,%s)" % (k, i, j), vtype=GRB.BINARY)

    ############################################################################################

    for k in courses:
        model.addConstr(x[j,i] <= quicksum(y[j,k] for k in types_hospitals))




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