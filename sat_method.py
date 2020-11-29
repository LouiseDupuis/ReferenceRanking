from itertools import combinaison

global unique_number
unique_number = 1

def initiate_x(comparaison_list, J, H, N):
    global unique_number
    result_dict = dict()
    for i in range(N):
        Xi = [comparaison_list[el][0][i] for el in range(J)] + [comparaison_list[el][1][i] for el in range(J)]
        for h in range(H):
            for k in Xi:
                result_dict[(i, h, k)] = unique_number
                unique_number += 1
    return result_dict

def initiate_y(comparaison_list, J, H, N):
    global unique_python
    result_dict = dict()
    sous_parties = []
    for taille in range(N+1):
        combi = list(combinations(list(range(N)), taille))
        sous_parties += combi
    for partie_a in sous_parties:
        for partie_b in sous_parties:
            result_dict[partie_a, partie_b] = unique_number
            unique_number += 1
    return result_dict


def initiate_d(comparaison_list, J, H, N):
    global unique_number
    result_dict = dict()
    for h in range(H):
        for l in range(H):
            result_dict[(h, l)] = unique_number
            unique_number += 1
    return result_dict


def initiate_s(comparaison_list, J, H, N):
    global unique_number
    result_dict = dict()
    for j in range(J):
        for h in range(H):
            result_dict[(j, h)] = unique_number
            unique_number += 1
    return result_dict

