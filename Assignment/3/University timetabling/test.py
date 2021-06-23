a = {'A','B','C','D'}
# def set2list(init_set):
#     result_list = []
#     temp_list = list(init_set)
#     for i in range(len(temp_list) - 1):
#         for j in temp_list[i + 1:]:
#             result_list.append({temp_list[i], j})
#     return result_list
#
# print(set2list(a))
a_1='A-1'
a_2='A-2'
b_1='B-1'
b_2='B-2'

test = [{(a_1,b_1),(a_2,b_2)},
        {(a_2,b_2),(a_1,b_1)}]
#
# print({(a_1,b_1),(a_2,b_2)} == {(a_2,b_2),(a_1,b_1)})
#
# for (a_1,b_1),(a_2,b_2) in test:
#     print((a_1,b_1),(a_2,b_2))

print(a.pop())