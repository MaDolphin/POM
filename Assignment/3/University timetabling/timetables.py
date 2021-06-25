from gurobipy import *
import networkx as nx
import math
import logging
import re
import pandas as pd

#logging file
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='log', filemode='w')

logger = logging.getLogger(__name__)

logger.info('start')

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

def list2pairList(init_list):
    result_list = []
    temp_list = sorted(init_list)
    for i in range(len(temp_list)):
        for j in range(len(temp_list)):
            if i != j:
                result_list.append((temp_list[i], temp_list[j]))
    return result_list

SEC_added = 0
#
SEC_violated = True

def solve(full_path_instance):
    global SEC_added
    global SEC_violated

    df_courses, df_rooms, dict_curricula, df_unavailability_constraints, days, periods = data_load(full_path_instance)

    # courses K
    courses = df_courses.index.to_list()

    # rooms R
    rooms = df_rooms.index.to_list()

    # curriculas Curriculas
    curriculas = dict_curricula.keys()

    logger.info(f'courses: {courses}')
    logger.info(f'df_rooms: {rooms}')
    logger.info(f'curricula: {curriculas}')

    # time_slots T
    time_slots = []
    for i in range(days):
        for j in range(periods):
            time_slots.append((i,j))

    logger.info(f'time slots: {time_slots}')
    # teachers Teachers
    teachers = df_courses['teacher'].unique()
    logger.info(f'teachers: {teachers}')

    # teacher teachs which courses
    teacher_course_pairs = {}
    for teacher in teachers:
        teacher_course_pairs[teacher] = df_courses[df_courses['teacher'] == teacher].index.to_list()
    logger.info(f'teacher teachs courses: {teacher_course_pairs}')

    # for course in which curricula
    courses_curriculas_pair = {}
    for course in courses:
        for curricula in curriculas:
            if course in dict_curricula[curricula]['members']:
                # temp_list.append(curricula)
                if course not in courses_curriculas_pair:
                    courses_curriculas_pair[course] = [curricula]
                else:
                    courses_curriculas_pair[course].append(curricula)
        # courses_curriculas_pair[course] = temp_list.copy()
        # temp_list.clear()
    logger.info(f'courses : [curricula]: {courses_curriculas_pair}')


    # course can be take place in which rooms K_r
    courses_rooms_pairs = {}
    temp_list = []
    for k in courses:
        for r in rooms:
            if df_courses.loc[k]['countOfStudents'] <= df_rooms.loc[r]['capacity']:
                temp_list.append(r)
        # if temp_list:
        courses_rooms_pairs[k] = temp_list.copy()
        temp_list.clear()
    logger.info(f'courses room pairs: {courses_rooms_pairs}')
    # for rooms which course can be take place in R_r
    # rooms_courses_pairs = {}
    # temp_list.clear()
    # for r in rooms:
    #     for k in courses:
    #         if df_courses.loc[k]['countOfStudents'] <= df_rooms.loc[r]['capacity']:
    #             temp_list.append(k)
    #     rooms_courses_pairs[r] = temp_list.copy()
    #     temp_list.clear()

    courses_courses_pairs = []
    for k_1 in range(len(courses)):
        for k_2 in range(k_1+1, len(courses)):
            courses_courses_pairs.append((courses[k_1],courses[k_2]))

    assert len(courses_courses_pairs) == len(courses)*(len(courses)-1)/2

    logger.info(f'courses courses pairs {courses_courses_pairs}')

    ############################################################################################

    model = Model("Timetables")
    # model.modelSense = GRB.MINIMIZE

    # whether course k takes place at time-slots (i,j)
    x = {}
    for k in courses:
        for (i,j) in time_slots:
            x[k,i,j] = model.addVar(
                name="x_%s_(%s,%s)" % (k, i, j),
                vtype=GRB.BINARY)

    # whether course k takes place on day i
    y = {}
    for k in courses:
        for i in range(days):
            y[k,i] = model.addVar(
                name="y_%s_(%s,_)" % (k, i),
                vtype=GRB.BINARY)

    # soft constraints
    penalty_assistant = {}
    for k_1, k_2 in courses_courses_pairs:
        for (i,j) in time_slots:
            penalty_assistant[k_1,k_2,i,j] = model.addVar(
                name="penalty_assistant_%s_%s_(%s,%s)" % (k_1,k_2, i, j),
                vtype=GRB.BINARY)

    # soft constraints
    penalty_students = {}
    for k_1, k_2 in courses_courses_pairs:
        for (i,j) in time_slots:
            penalty_students[k_1,k_2,i,j] = model.addVar(
                name="penalty_students_%s_%s_(%s,%s)" % (k_1,k_2,i,j),
                vtype=GRB.BINARY)

    # soft constraints
    penalty_days = {}
    for k in courses:
        penalty_days[k] = model.addVar(
            name="penalty_days_%s" % (k),
            vtype=GRB.CONTINUOUS)

    # soft constraints
    penalty_teachers = {}
    for index, row in df_unavailability_constraints.iterrows():
        k = index
        i = row[0]
        j = row[1]
        penalty_teachers[k,i,j] = model.addVar(
            name="penalty_teachers_%s_(%s,%s)" % (k, i, j),
            vtype=GRB.BINARY)

    # penalty rate
    c_assistant = 1.0
    c_students = 0.1
    c_days = 0.1
    c_teachers = 10.0

    ############################################################################################

    # Constr_1: For every course, a given number <l_k> of lectures have to be scheduled
    for k in courses:
        model.addConstr(quicksum(x[k,i,j] for (i,j) in time_slots) ==
                        df_courses.loc[k]['countOfLectures'])

    # Constr_2: The lectures of a given course have to take place on at least <d_k> different days
    # a). with penalty model:
    # *** using 'penalty_days[k]' for course taking place less than <d_k> different days ***
    for k in courses:
        model.addConstr(quicksum(y[k,i] for i in range(days)) >=
                        df_courses.loc[k]['minWorkingDays'] - penalty_days[k])

    # b). no penalty model:
    # for k in courses:
    #     model.addConstr(quicksum(y[k,i] for i in range(days)) >=
    #                     df_courses.loc[k]['minWorkingDays'])

    # Constr_2.1: Linking between x[k,i,j] and y[k,i]
    # for k in courses:
    #     for i in range(days):
    #         model.addConstr(quicksum(x[k,i,j] for j in range(periods)) == quicksum(y[k,i]*x[k,i,j] for j in range(periods)))

    for k in courses:
        for i in range(days):
            for j in range(periods):
                model.addConstr(x[k,i,j] <= y[k,i])

    for k in courses:
        for i in range(days):
            model.addConstr(y[k,i] <= quicksum(x[k,i,j] for j in range(periods)))



    # Constr_3: Courses taught by the same teacher can not take place in the same time-slot
    # a). with penalty model:
    # *** using 'penalty_assistant[k_1,k_2,i,j]' for the same teacher taking place in the same time-slot ***
    for teacher in teachers:
        for (i,j) in time_slots:
            t_courses = teacher_course_pairs[teacher]
            if len(t_courses) > 1:
                for k_1, k_2 in list2pairList(t_courses):
                    if (k_1,k_2) in courses_courses_pairs:
                        model.addConstr((x[k_1,i,j] + x[k_2,i,j]) <= 1 + penalty_assistant[k_1,k_2,i,j])

    # b). no penalty model:
    # for teacher in teachers:
    #     for (i,j) in time_slots:
    #         model.addConstr(quicksum(x[k, i, j] for k in teacher_course_pairs[teacher]) <= 1)



    # Constr_4: Courses that are part of the same curriculum can not take place in the same time-slot
    # a). with penalty model:
    # *** using 'penalty_students[k_1,k_2,i,j]' for courses k of the same curriculum taking place in the same time-slot ***
    for curricula in curriculas:
        for (i,j) in time_slots:
            c_courses = dict_curricula[curricula]['members']
            if len(c_courses) > 1:
                for k_1, k_2 in list2pairList(c_courses):
                    if (k_1, k_2) in courses_courses_pairs:
                        model.addConstr((x[k_1,i,j] + x[k_2,i,j]) <= 1 + penalty_students[k_1,k_2,i,j])

    # b). no penalty model:
    # for curricula in curriculas:
    #     for (i,j) in time_slots:
    #         model.addConstr(quicksum(x[k,i,j] for k in dict_curricula[curricula]['members']) <= 1)



    # Constr_5: For a variety of reasons, some unavailability constraints are given,
    # such that courses <k> can not take place in some time-slots (i,j)
    # a). with penalty model:
    # *** using 'penalty_teachers[k,i,j]' for assignment the course on time-slot that teacher don't like ***
    for index, row in df_unavailability_constraints.iterrows():
        k = index
        i = row[0]
        j = row[1]
        model.addConstr(x[k,i,j] <= 0 + penalty_teachers[k,i,j])

    # b). no penalty model:
    # for index, row in df_unavailability_constraints.iterrows():
    #     k = index
    #     i = row[0]
    #     j = row[1]
    #     model.addConstr(x[k,i,j] == 0)



    ############################################################################################

    model.setObjective(
            0.0 + c_assistant * quicksum(penalty_assistant[k_1,k_2,i,j]
                                     for k_1, k_2 in courses_courses_pairs
                                     for (i,j) in time_slots) +
            c_students * quicksum(penalty_students[k_1,k_2,i,j]
                                  for k_1, k_2 in courses_courses_pairs
                                  for (i,j) in time_slots) +
            c_days * quicksum(penalty_days[k]
                              for k in courses) +
            c_teachers * quicksum(penalty_teachers[index,row[0],row[1]]
                                  for index, row in df_unavailability_constraints.iterrows()),
        GRB.MINIMIZE
    )

    model.update()
    model.write('Timetables.lp')

    ############################################################################################

    # Printing solution and objective value
    def printSolution():
        if model.status == GRB.OPTIMAL:
            print('\n objective: %g\n' % model.ObjVal)
            print("Selected following matching:")
            for k in courses:
                for (i, j) in time_slots:
                    if x[k, i, j].x == 1:
                        print("x_%s_(%s,%s)" % (k, i, j))

            for k in courses:
                if penalty_days[k].x >= 1:
                    print("penalty_days_%s" % (k))

            for k_1, k_2 in courses_courses_pairs:
                for (i, j) in time_slots:
                    if penalty_assistant[k_1, k_2, i, j].x == 1:
                        print("penalty_assistant_%s_%s_(%s,%s)" % (k_1, k_2, i, j))

            for k_1, k_2 in courses_courses_pairs:
                for (i, j) in time_slots:
                    if penalty_students[k_1, k_2, i, j].x == 1:
                        print("penalty_students_%s_%s_(%s,%s)" % (k_1, k_2, i, j))

            for index, row in df_unavailability_constraints.iterrows():
                k = index
                i = row[0]
                j = row[1]
                if penalty_teachers[k, i, j].x == 1:
                    print("penalty_teachers_%s_(%s,%s)" % (k, i, j))

        else:
            print("No solution!")




    # define a so-called "callback" which in each node of the B&C tree (not only
    # at the root node) adds violated subtour elimination constraints
    def separateRoom(model, where):
        global SEC_added
        if where == GRB.Callback.MIPSOL:
            rel = model.cbGetSolution(x)
            # logger.info('***********')
            # logger.info(rel)
            # logger.info('***********')

            def createGraph(i,j):

                courses_with_time = []
                for k in courses:
                    if round(rel[k, i, j]) == 1:
                        courses_with_time.append((k,i,j))

                edge_rooms_t = []
                for room in rooms:
                    edge_rooms_t.append((room, 'terminal'))

                edge_k_rooms = []
                for k in courses:
                    # if k in courses_courses_pairs:
                    for room in courses_rooms_pairs[k]:
                        if room != '':
                            edge_k_rooms.append((k, room))

                # check for violate Room (max flow algorithm)
                G = nx.DiGraph()

                G.add_node('start')
                G.add_node('terminal')
                G.add_nodes_from(courses)
                G.add_nodes_from(rooms)

                for k in courses:
                    G.add_edge('start', k, capacity=round(rel[k, i, j]))

                G.add_edges_from(edge_rooms_t, capacity=1)
                G.add_edges_from(edge_k_rooms, capacity=1)

                # print(G.nodes())

                flow = nx.maximum_flow(G, 'start', 'terminal')

                return courses_with_time, flow[0]

            a, b = 0, 0
            for (i, j) in time_slots:

                courses_with_time, flow_max = createGraph(i,j)

                if len(courses_with_time) > flow_max:
                    model.cbLazy(quicksum(x[k, i, j] for (k, _, _) in courses_with_time) <= flow_max)
                    SEC_added = SEC_added + 1
                    courses_with_time.clear()
                    a += 1
                    # print("True")
                    break
                else:
                    courses_with_time.clear()
                    # print("False")
                    b += 1
                    continue

            print('violated:', a, 'correct:', b)


    ############################################################################################

    # indicate that some constraints are "lazily" added to the model
    model.params.LazyConstraints = 1
    model.optimize(separateRoom)
    print("Added", SEC_added, "SECs.")

    # model.optimize()


    return model

solve('comp01.ctt')