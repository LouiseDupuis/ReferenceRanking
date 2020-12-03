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
        for h_prime in range(H):
            result_dict[(h, h_prime)] = unique_number
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


def clause_1(X, J, H, N):
    clause = []
    for i in range(N):
        Xi = [comparaison_list[el][0][i] for el in range(J)] + [comparaison_list[el][1][i] for el in range(J)]
        for h in range(H):
            for k in Xi:
                for k_prime in Xi:
                    if k > k_prime:
                        clause.append([-X[(i, h, k_prime)], X[(i, h, k)]])
    return clause
    
def clause_2a(D, J, H, N):
    clause = []
    for h in range(H):
        for h_prime in range(h + 1, H):
            clause.append([D[(h, h_prime)], D[(h_prime, h)]])
    return clause


def clause_2b(X, D, J, H, N):
    clause = []
    for i in range(N):
        Xi = [comparaison_list[el][0][i] for el in range(J)] + [comparaison_list[el][1][i] for el in range(J)]
        for k in Xi:
            for h in range(H):
                for h_prime in range(h_prime):
                    if h != h_prime:
                        clause.append([X[(i, h_prime, k)], -X[(i, h, k)], -D[(h, h_prime)]])
    return clause

def clause_3a(Y, J, H, N ):
    clause = []
    for a,b in Y.keys():
        clause.append([Y[(a,b)], Y[(b,a)]])
    return clause


def clause_3b(Y, J, H, N):
    clause = []
    for a, b in Y.keys():
        if set(a).issubset(set(b)):
            clause.append([Y[(b, a)]])
    return clause

def clause_3c(Y, J, H, N):
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


def clause_4a(Y, X, Z, J, H, N, comparaison_list):
    clause = []
    for partie_a, partie_b in Y:
        for j in range(J):
            for h in range(H):
                clause_parts = []
                for i in range(N):
                    if i not in partie_a:
                        clause_parts.append(X[(i, h, comparaison_list[j][0][i])])
                    if i in partie_b:
                        clause_parts.append(-X[(i, h, comparaison_list[j][1][i])])
                clause_parts.append(Y[(partie_a, partie_b)])
                clause_parts.append(-Z[(j, h)])
                clause.append(clause_parts)
    return clause
    
def clause_4b(Y, X, Z_prime, J, H, N, comparaison_list):
    clause = []
    for partie_a, partie_b in Y:
        for j in range(J):
            for h in range(H):
                clause_parts = []
                for i in range(N):
                    if i not in partie_a:
                        clause_parts.append(X[(i, h, comparaison_list[j][1][i])])
                    if i in partie_b:
                        clause_parts.append(-X[(i, h, comparaison_list[j][0][i])])
                clause_parts.append(Y[(partie_a, partie_b)])
                clause_parts.append(-Z_prime[(j, h)])
                clause.append(clause_parts)
    return clause
    
def clause_4c(Y, X, Z_prime, J, H, N, comparaison_list):
    clause = []
    for partie_a, partie_b in Y:
        for j in range(J):
            for h in range(H):
                clause_parts = []
                for i in range(N):
                    if i in partie_a:
                        clause_parts.append(-X[(i, h, comparaison_list[j][0][i])])
                    else:
                        clause_parts.append(X[(i, h, comparaison_list[j][0][i])])
                    if i in partie_b:
                        clause_parts.append(-X[(i, h, comparaison_list[j][1][i])])
                    else:
                        clause_parts.append(X[(i, h, comparaison_list[j][0][i])])
                clause_parts.append(-Y[(partie_b, partie_a)])
                clause_parts.append(Z_prime[(j, h)])
                clause.append(clause_parts)
    return clause

# def clause_4d(S, J, H, N):


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



