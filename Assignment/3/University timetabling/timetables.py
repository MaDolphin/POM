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
                start_flag = True
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

    # curriculas Curriculas
    curriculas = dict_curricula.keys()

    # time_slots T
    time_slots = []
    for i in range(days):
        for j in range(periods):
            time_slots.append((i,j))

    # teachers Teachers
    teachers = df_courses['teacher'].unique()

    # teacher teachs which courses
    teacher_course_pairs = {}
    for teacher in teachers:
        teacher_course_pairs[teacher] = set(df_courses[df_courses['teacher'] == teacher].index)

    # for course in which curricula
    courses_curriculas_pair = {}
    set_temp = set()
    for course in courses:
        for curricula in curriculas:
            if course in dict_curricula[curricula]['members']:
                set_temp.add(curricula)
        courses_curriculas_pair[course] = set_temp.copy()
        set_temp.clear()

    # course can be take place in which rooms K_r
    courses_rooms_pairs = {}
    set_temp.clear()
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
    # model.modelSense = GRB.MINIMIZE

    # whether course k takes place at time-slots (i,j)
    x = {}
    for k in courses:
        for (i,j) in time_slots:
            x[k,i,j] = model.addVar(name="x_%s_(%s,%s)" % (k, i, j), vtype=GRB.BINARY)

    # soft constraints
    penalty_assistant = model.addVar(name="penalty_assistant", vtype=GRB.INTEGER)

    # soft constraints
    # whether k is penalized, 1 is penalized, 0 is not penalized
    penalty_students = {}
    for k in courses:
        penalty_students[k] = model.addVar(name="penalty_students_%s" % (k), vtype=GRB.BINARY)

    # soft constraints
    penalty_days = model.addVar(name="penalty_days", vtype=GRB.INTEGER)

    # soft constraints
    penalty_teachers = model.addVar(name="penalty_teachers", vtype=GRB.INTEGER)

    # penalty rate
    c_assistant = 1.0
    c_students = 0.1
    c_days = 0.1
    c_teachers = 10

    ############################################################################################

    # For every course, a given number <l_k> of lectures have to be scheduled
    for k in courses:
        model.addConstr(quicksum(x[k,i,j] for (i,j) in time_slots) ==
                        df_courses.loc[k]['countOfLectures'])

    # The lectures of a given course have to take place on at least <d_k> different days
    # *** using 'penalty_days' for course taking place less than <d_k> different days ***
    for k in courses:
        model.addConstr(quicksum(x[k,i,j] for i in range(days)) >=
                        df_courses.loc[k]['minWorkingDays'] - penalty_days)

    # Courses taught by the same teacher can not take place in the same time-slot
    # *** using 'penalty_assistant' for the same teacher taking place in the same time-slot ***
    for teacher in teachers:
        for (i,j) in time_slots:
            model.addConstr(quicksum(x[k,i,j] for k in teacher_course_pairs[teacher]) <= 1 + penalty_assistant)

    # Courses that are part of the same curriculum can not take place in the same time-slot
    # *** using 'penalty_students[k]' for courses k of the same curriculum taking place in the same time-slot ***
    for curricula in curriculas:
        for (i,j) in time_slots:
            model.addConstr(quicksum(x[k,i,j] for k in dict_curricula[curricula]['members']) <=
                            1 + quicksum(penalty_students[k] for k in dict_curricula[curricula]['members']))

    # For a variety of reasons, some unavailability constraints are given,
    # such that courses <k> can not take place in some time-slots (i,j)
    # *** using 'penalty_teachers' for assignment the course on time-slot that teacher don't like ***
    for index, row in df_unavailability_constraints.iterrows():
        k = index
        i = row[0]
        j = row[1]
        model.addConstr(x[k,i,j] <= 0 + penalty_teachers)

    ############################################################################################


    model.setObjective(
        0.0 + c_assistant * penalty_assistant +
            c_students * quicksum(penalty_students[k] for k in courses) +
            c_days * penalty_days +
            c_teachers * penalty_teachers,
        GRB.MINIMIZE
    )

    model.update()
    model.write('Timetables.lp')
    model.optimize()
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

solve('comp02.ctt')