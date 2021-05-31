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
        print(dataFrame[i])

    df_hospitals = dataFrame[0]
    df_existing_hospitals = dataFrame[1]
    df_cities = dataFrame[2]
    df_cities_minimum = dataFrame[3]

    return df_hospitals, df_existing_hospitals, df_cities, df_cities_minimum

def solve(fileName):
    df_hospitals, df_existing_hospitals, df_cities, df_cities_minimum = data_load(fileName)

    model = Model("Hospitalnetwork")
    return model

solve(fileName)