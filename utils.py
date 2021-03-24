from itertools import combinations
import random
from RMP import RMP
import os



def generate_random_RMP_learning_set(J, N):
    result = []
    for _ in range(J):
        p = [random.random() for i in range(N)]
        n = [random.random() for i in range(N)]
        result.append((p,n))
    return result



def generate_RMP_learning_set(J, N, H, rounded=True):
    criteria_weights = [random.random() for i in range(N)]
    sum_weights = sum(criteria_weights)
    criteria_weights = [weight / sum_weights for weight in criteria_weights]

    coalition_importance = dict()
    sous_parties = []
    for taille in range(N + 1):
        combi = list(combinations(list(range(N)), taille))
        sous_parties += combi

    for partie_a in sous_parties:
        a_weights = sum([criteria_weights[i] for i in partie_a])
        for partie_b in sous_parties:
            b_weights = sum([criteria_weights[i] for i in partie_b])
            if a_weights >= b_weights:
                coalition_importance[partie_a, partie_b] = 1
            else:
                coalition_importance[partie_a, partie_b] = -1

    reference_points = [[0 for _ in range(N)] for _ in range(H)]
    for i in range(N):
        uniform_picks = sorted([random.random() for _ in range(H)])
        for h in range(H):
            reference_points[h][i] = uniform_picks[h]

    RMP_model = RMP(reference_points, coalition_importance)
    print(RMP_model.reference_points)
    result = []
    comparison_count = 0
    while comparison_count < J:
        if rounded:
            p = [ round(random.random(), 1) for i in range(N)]
            n = [ round(random.random(), 1) for i in range(N)]
        else:
            p = [ random.random() for i in range(N)]
            n = [ random.random() for i in range(N)]
        comparison = RMP_model.compare(p, n)
        if not comparison[1]:
            if comparison[0]:
                result.append((p, n))
            else:
                result.append((n, p))
            comparison_count += 1
    return result


def marco_mus_solver(intput_cnf, output_file):
    os.system("python3 MARCO/marco.py " + str(intput_cnf + " -v >" + str(output_file)))