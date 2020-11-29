from itertools import combinations

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
    global unique_number
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

def initiate_z(comparaison_list, J, H, N):
    global unique_number
    result_dict = dict()
    for j in range(J):
        for h in range(H):
            result_dict[(j, h)] = unique_number
            unique_number += 1
    return result_dict
    
def initiate_z_prime(comparaison_list, J, H, N):
    global unique_number
    result_dict = dict()
    for j in range(J):
        for h in range(H):
            result_dict[(j, h)] = unique_number
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


def clause_3a(Y, comparaison_list, J, H, N ):
    clause = []
    for a,b in Y.keys():
        clause.append([Y[(a,b)], Y[(b,a)]])
    return clause

def clause_3b(Y, comparaison_list, J, H, N):
    clause = []
    for a, b in Y.keys():
        if set(a).issubset(set(b)):
            clause.append([Y[(b, b)]])
    return clause

def clause_3c(Y, comparaison_list, J, H, N):
    clause = []
    sous_parties = []
    for taille in range(N + 1):
        combi = list(combinations(list(range(N)), taille))
        sous_parties += combi

    for a in sous_parties:
        for b in sous_parties:
            for c in sous_parties:
                clause.append([ -Y[(a, b)], -Y[(b, c)], Y[(a, c)]])
    return clause

def clause_5a(Z, S,comparaison_list, J, H, N):
    clauses = []
    for j in range(J):
        for h in range(H):
            for h_prime in range(h + 1, H):
                clauses.append([Z[j, h], -S[j, h_prime]])
    return clauses

def clause_5b(Z_prime, S,comparaison_list, J, H, N):
    clauses = []
    for j in range(J):
        for h in range(H):
            for h_prime in range(h + 1, H):
                clauses.append([Z_prime[j, h], -S[j, h_prime]])
    return clauses


def clause_5c(Z_prime, S,comparaison_list, J, H, N):
    clauses = []
    for j in range(J):
        for h in range(H):
            clauses.append([ - Z_prime[j, h], -S[j, h]])
    return clauses

def clause_6( S, comparaison_list, J, H, N):
    clauses = []
    for j in range(J):
        clauses.append([ S[j, h] for h in range(H)])
    return clauses


