#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 22:56:53 2020

@author: luebbecke
"""

# easy

n=200 #items
m=150 #bins

b = 100 #capacity
a = [26, 10, 75, 42, 9, 13, 73, 61, 61, 28, 38, 72, 19, 37, 20, 18, 22, 26, 63, 29, 38, 42, 5, 5, 28, 52, 52, 27, 18, 44, 8, 42, 71, 28, 72, 39, 73, 36, 54, 46, 50, 66, 59, 65, 21, 52, 74, 11, 18, 72, 12, 53, 9, 23, 7, 54, 47, 45, 13, 4, 67, 70, 58, 25, 11, 3, 44, 45, 30, 17, 46, 18, 75, 54, 18, 74, 41, 22, 27, 28, 75, 40, 7, 8, 57, 4, 6, 46, 13, 11, 30, 36, 42, 39, 6, 40, 67, 12, 16, 41, 4, 22, 70, 47, 61, 17, 25, 73, 44, 17, 60, 36, 16, 2, 75, 1, 40, 15, 62, 38, 56, 25, 5, 8, 1, 63, 66, 57, 3, 72, 12, 26, 63, 3, 38, 7, 60, 38, 55, 9, 9, 32, 30, 50, 21, 75, 29, 43, 65, 58, 50, 56, 58, 10, 44, 6, 14, 7, 49, 17, 63, 17, 33, 64, 62, 65, 1, 13, 28, 4, 56, 67, 54, 27, 14, 57, 52, 66, 64, 25, 10, 72, 26, 11, 9, 32, 21, 22, 34, 4, 56, 64, 9, 40, 35, 31, 15, 16, 58, 48]


import binpackingmodel
binpackingmodel.solve(m,a,b)


"""
import makespanscheduling
makespanscheduling.solve(m,a,b)
"""
