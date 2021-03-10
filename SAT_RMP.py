import os, sys
from itertools import combinations
from bidict import bidict
import random
import pylgl


class RMP:

    def __init__(self, reference_points, coalition_importance):
        """
            reference_points : liste de listes (indice : critère, valeur : evaluation du critère)
            hypothèse : les evaluations des critère sont numériques
            criteria : listes des critères
            coalition_importance : est un dictionnaire qui contient toutes le svaribales Y(a,b) pour toutes les coalitiosn a,b de critères
        """
        self.reference_points = reference_points
        self.criteria = list(range(len(reference_points[0])))
        self.coalition_importance = coalition_importance

    def __str__(self):
        # function to print a summary of a RMP model
        print("============================ RMP Model ==========================")
        print("Number of Reference Points : ", len(self.reference_points))
        print()
        i = 0
        for ref in self.reference_points:
            print(i, " ", ref)
            i += 1
        print()
        return ''

    def is_more_important_coalition(self, coalition_1, coalition_2):
        """
            fonction de comparaison de domination de deux ensembles de critères
        """
        # print('coal_1', coalition_1, 'coal_2', coalition_2)
        return self.coalition_importance[(coalition_1, coalition_2)] > 0

    def dominant_criteria_set(self, a, reference_point):
        """
            compute c(a,rh)={i∈N:ai ≥rih}
        """
        result = []
        for criterion in self.criteria:
            if a[criterion] >= reference_point[criterion]:
                result.append(criterion)
        return tuple(sorted(result))

    def domination(self):
        for rh in self.reference_points:
            for rh_prime in [el for el in self.reference_points if el != rh]:
                index = 0
                while rh[index] == rh_prime[index] and index < len(rh):
                    index += 1
                if rh[index] > rh_prime[index]:
                    for i in range(index, len(rh)):
                        if rh[i] < rh_prime[i]:
                            return False
                else:
                    for i in range(index, len(rh)):
                        if rh[i] > rh_prime[i]:
                            return False
        return True

    def compare(self, object_1, object_2):
        """
            returns a tuple ( is_preferred(object_1, object_2), is_indifferent(object_1, object_2))
        """
        for reference_point in self.reference_points:
            # print(reference_point)
            coalition_1 = self.dominant_criteria_set(object_1, reference_point)
            coalition_2 = self.dominant_criteria_set(object_2, reference_point)
            if not self.is_more_important_coalition(coalition_2, coalition_1):
                # 1 > 2
                return True, False
            elif not self.is_more_important_coalition(coalition_1, coalition_2):
                # 1 < 2
                return False, False
        return False, True


class SatRmp:
    instance_id = 1

    def __init__(self, comparaison_list, J, H, N):
        """

        """
        self.unique_number = 1
        self.id = SatRmp.instance_id
        SatRmp.instance_id += 1

        self.comparaison_list = comparaison_list
        self.J = J
        self.H = H
        self.N = N

        self.X = None
        self.Y = None
        self.Z = None
        self.Z_prime = None
        self.D = None
        self.S = None
        self.clauses = None
        self.SAT_result = None
        self.RMP_model = None
        self.comparaison_to_clause = {j: [] for j in range(self.J)}
        self.clause_index = 0
        self.reset()

    def reset(self):
        self.X = self.initiate_x()
        self.Y = self.initiate_y()
        self.Z = self.initiate_z()
        self.Z_prime = self.initiate_z_prime()
        self.D = self.initiate_d()
        self.S = self.initiate_s()
        self.clauses = self.initiate_clauses()

    def initiate_x(self):
        result_dict = bidict()
        for i in range(self.N):
            Xi = [self.comparaison_list[el][0][i] for el in range(self.J)] + [self.comparaison_list[el][1][i] for el in
                                                                              range(self.J)]
            for h in range(self.H):
                for k in Xi:
                    result_dict[(i, h, k)] = self.unique_number
                    self.unique_number += 1
        return result_dict

    def initiate_y(self):
        result_dict = bidict()
        sous_parties = []
        for taille in range(self.N + 1):
            combi = list(combinations(list(range(self.N)), taille))
            sous_parties += combi
        for partie_a in sous_parties:
            for partie_b in sous_parties:
                result_dict[partie_a, partie_b] = self.unique_number
                self.unique_number += 1
        return result_dict

    def initiate_z(self):
        result_dict = bidict()
        for j in range(self.J):
            for h in range(self.H):
                result_dict[(j, h)] = self.unique_number
                self.unique_number += 1
        return result_dict

    def initiate_z_prime(self):
        result_dict = bidict()
        for j in range(self.J):
            for h in range(self.H):
                result_dict[(j, h)] = self.unique_number
                self.unique_number += 1
        return result_dict

    def initiate_d(self):
        result_dict = bidict()
        for h in range(self.H):
            for h_prime in range(self.H):
                if h != h_prime:
                    result_dict[(h, h_prime)] = self.unique_number
                    self.unique_number += 1
        return result_dict

    def initiate_s(self):
        result_dict = bidict()
        for j in range(self.J):
            for h in range(self.H):
                result_dict[(j, h)] = self.unique_number
                self.unique_number += 1
        return result_dict

    def clause_1(self):
        clause = []
        for i in range(self.N):
            Xi = [self.comparaison_list[el][0][i] for el in range(self.J)] + [self.comparaison_list[el][1][i] for el in
                                                                              range(self.J)]
            for h in range(self.H):
                for k in Xi:
                    for k_prime in Xi:
                        if k > k_prime:
                            clause.append([-self.X[(i, h, k_prime)], self.X[(i, h, k)]])
                            self.clause_index += 1
        return clause

    def clause_2a(self):
        clause = []
        for h_prime in range(self.H):
            for h in range(h_prime + 1, self.H):
                clause.append([self.D[(h, h_prime)], self.D[(h_prime, h)]])
                self.clause_index += 1
        return clause

    def clause_2b(self):
        clause = []
        for i in range(self.N):
            Xi = [self.comparaison_list[el][0][i] for el in range(self.J)] + [self.comparaison_list[el][1][i] for el in
                                                                              range(self.J)]
            for h in range(self.H):
                for h_prime in range(self.H):
                    for k in Xi:
                        if h != h_prime:
                            clause.append([self.X[(i, h_prime, k)], -self.X[(i, h, k)], -self.D[(h, h_prime)]])
                            self.clause_index += 1
        return clause

    def clause_3a(self):
        clause = []
        for partie_a, partie_b in self.Y:
            clause.append([self.Y[(partie_a, partie_b)], self.Y[(partie_b, partie_a)]])
            self.clause_index += 1
        return clause

    def clause_3b(self):
        clause = []
        for partie_a, partie_b in self.Y:
            if set(partie_b).issubset(set(partie_a)):
                clause.append([self.Y[(partie_a, partie_b)]])
                self.clause_index += 1
        return clause

    def clause_3c(self):
        clause = []
        sous_parties = []
        for taille in range(self.N + 1):
            combi = list(combinations(list(range(self.N)), taille))
            sous_parties += combi

        for a in sous_parties:
            for b in sous_parties:
                for c in sous_parties:
                    clause.append([-self.Y[(a, b)], -self.Y[(b, c)], self.Y[(a, c)]])
                    self.clause_index += 1
        return clause

    def clause_4a(self):
        clauses = []
        for j in range(self.J):
            clauses.append([self.S[j, h] for h in range(self.H)])
            self.comparaison_to_clause[j].append(self.clause_index)
            self.clause_index += 1
        return clauses

    def clause_4b(self):
        clauses = []
        for j in range(self.J):
            for h in range(self.H):
                for h_prime in range(0, h + 1):
                    clauses.append([self.Z[j, h_prime], -self.S[j, h]])
                    self.comparaison_to_clause[j].append(self.clause_index)
                    self.clause_index += 1
        return clauses

    def clause_4c(self):
        clauses = []
        for j in range(self.J):
            for h_prime in range(self.H):
                for h in range(h_prime + 1, self.H):
                    clauses.append([self.Z_prime[j, h_prime], -self.S[j, h]])
                    self.comparaison_to_clause[j].append(self.clause_index)
                    self.clause_index += 1
        return clauses

    def clause_4d(self):
        clauses = []
        for j in range(self.J):
            for h in range(self.H):
                clauses.append([-self.Z_prime[j, h], -self.S[j, h]])
                self.comparaison_to_clause[j].append(self.clause_index)
                self.clause_index += 1
        return clauses

    def clause_5a(self):
        clause = []
        sous_parties = []
        for taille in range(self.N + 1):
            combi = list(combinations(list(range(self.N)), taille))
            sous_parties += combi

        for partie_a in sous_parties:
            for partie_b in sous_parties:
                for j in range(self.J):
                    for h in range(self.H):
                        clause_parts = []
                        for i in range(self.N):
                            if i not in partie_a:
                                clause_parts.append(self.X[(i, h, self.comparaison_list[j][0][i])])
                            if i in partie_b:
                                clause_parts.append(-self.X[(i, h, self.comparaison_list[j][1][i])])
                        clause_parts.append(self.Y[(partie_a, partie_b)])
                        clause_parts.append(-self.Z[(j, h)])
                        clause.append(clause_parts)
                        self.comparaison_to_clause[j].append(self.clause_index)
                        self.clause_index += 1
        return clause

    def clause_5b(self):
        clause = []
        sous_parties = []
        for taille in range(self.N + 1):
            combi = list(combinations(list(range(self.N)), taille))
            sous_parties += combi

        for partie_a in sous_parties:
            for partie_b in sous_parties:
                for j in range(self.J):
                    for h in range(self.H):
                        clause_parts = []
                        for i in range(self.N):
                            if i not in partie_a:
                                clause_parts.append(self.X[(i, h, self.comparaison_list[j][1][i])])
                            if i in partie_b:
                                clause_parts.append(-self.X[(i, h, self.comparaison_list[j][0][i])])
                        clause_parts.append(self.Y[(partie_a, partie_b)])
                        clause_parts.append(-self.Z_prime[(j, h)])
                        clause.append(clause_parts)
                        self.comparaison_to_clause[j].append(self.clause_index)
                        self.clause_index += 1
        return clause

    def ignore(self):
        clause = []
        sous_parties = []
        for taille in range(self.N + 1):
            combi = list(combinations(list(range(self.N)), taille))
            sous_parties += combi

        for partie_a in sous_parties:
            for partie_b in sous_parties:
                for j in range(self.J):
                    for h in range(self.H):
                        clause_parts = []
                        for i in range(self.N):
                            if i in partie_a:
                                clause_parts.append(-self.X[(i, h, self.comparaison_list[j][0][i])])
                            if i not in partie_a:
                                clause_parts.append(self.X[(i, h, self.comparaison_list[j][0][i])])
                            if i in partie_b:
                                clause_parts.append(-self.X[(i, h, self.comparaison_list[j][1][i])])
                            if i not in partie_b:
                                clause_parts.append(self.X[(i, h, self.comparaison_list[j][1][i])])
                        clause_parts.append(-self.Y[(partie_b, partie_a)])
                        clause_parts.append(self.Z_prime[(j, h)])
                        clause.append(clause_parts)
        return clause

    def clause_5c(self):
        clause = []
        sous_parties = []
        for taille in range(self.N + 1):
            combi = list(combinations(list(range(self.N)), taille))
            sous_parties += combi

        for partie_a in sous_parties:
            for partie_b in sous_parties:
                for j in range(self.J):
                    for h in range(self.H):
                        clause_parts = []
                        for i in range(self.N):
                            if i not in partie_a:
                                clause_parts.append(self.X[(i, h, self.comparaison_list[j][0][i])])
                            if i in partie_b:
                                clause_parts.append(-self.X[(i, h, self.comparaison_list[j][1][i])])
                        clause_parts.append(-self.Y[(partie_b, partie_a)])
                        clause_parts.append(self.Z_prime[(j, h)])
                        clause.append(clause_parts)
                        self.comparaison_to_clause[j].append(self.clause_index)
                        self.clause_index += 1
        return clause

    def initiate_clauses(self):
        self.structure_clauses_index = len(self.clause_1() +  self.clause_2a() +  self.clause_2b()
                                           + self.clause_3a() +  self.clause_3b() + self.clause_3c())

        clauses =  self.clause_1() +  self.clause_2a() +  self.clause_2b() +  self.clause_3a() +  self.clause_3b() + self.clause_3c()
        clauses +=  self.clause_4a() + self.clause_4b() + self.clause_4c() + self.clause_4d()
        clauses +=  self.clause_5a() + self.clause_5b() + self.clause_5c()
        self.clauses = clauses
        print("len", self.structure_clauses_index, len(self.clauses), self.clause_index)
        return clauses

    def get_clause_numbers(self, j):
        """
        Returns the index of the clauses associated with comparison j of the comparison list
        """

        indexes = dict()
        for clause, i in self.clauses_index.items():
            indexes[clause] = i + j  # pas j !! bcp plus compliqué
        return indexes

    def get_comparison_from_clause(self, index):
        """
        Returns the index j of the comparison that relates to the clause with index i
        """

        if index < self.structure_clauses_index:
            raise Exception("A structure clause index was provided ")
        else:
            current_index = self.structure_clauses_index
            for clause, i in self.clauses_index.items():
                if index <= i :# inferieur ou égal ????
                    j = i - current_index
                    return j
                else:
                    current_index = i
        raise Exception("The index provided ", index, " is greater than the maximum index ", len(self.clauses))



    def adjust_intervals(self, interval_1, interval_2):
        if interval_1[1] < interval_2[0]:
            raise Exception("Couldn't create RMP model")
        elif interval_1[0] >= interval_2[1]:
            return interval_1, interval_2
        elif interval_1[1] <= interval_2[1]:
            intersection = [max(interval_1[0], interval_2[0]), min(interval_1[1], interval_2[1])]
            middle = intersection[0] + (intersection[1] - intersection[0]) / 2
            return [middle, intersection[1]], [intersection[0], middle]
        elif interval_2[1] <= interval_1[1]:
            intersection = [max(interval_1[0], interval_2[0]), min(interval_1[1], interval_2[1])]
            middle = intersection[0] + (intersection[1] - intersection[0]) / 2
            return [middle, interval_1[1]], [interval_2[0], middle]

    def run_SAT(self):
        self.SAT_result = pylgl.solve(self.clauses)

    def create_RMP_model(self):
        assert self.SAT_result != 'UNSAT', "Problem is UNSAT"
        SAT_X, SAT_Y, SAT_D = dict(), dict(), dict()

        # récupérer les x, y et les d donnés par le solveur SAT
        for variable in self.SAT_result:
            if abs(int(variable)) in self.X.inverse:
                SAT_X[self.X.inverse[abs(int(variable))]] = int(variable)
            if abs(int(variable)) in self.Y.inverse:
                SAT_Y[self.Y.inverse[abs(int(variable))]] = int(variable)
            if abs(int(variable)) in self.D.inverse:
                SAT_D[self.D.inverse[abs(int(variable))]] = int(variable)

        # contruire les profils de référence
        reference_points = []

        for h in range(self.H):
            reference_point_interval = []
            for i in range(self.N):
                min_value, max_value = 0, 1
                Xi = [self.comparaison_list[el][0][i] for el in range(self.J)] + [self.comparaison_list[el][1][i] for el
                                                                                  in range(self.J)]
                for k in Xi:
                    if SAT_X[i, h, k] > 0:
                        max_value = min(max_value, k)
                    else:
                        min_value = max(min_value, k)
                if min_value >= max_value:
                    raise Exception("Couldn't create RMP model")
                # construction des intervals de valeurs possible pour les points de references
                reference_point_interval.append([min_value, max_value])
            reference_points.append(reference_point_interval)

        # Ajustement des intervals pour respecter la dominance entre points de refenrences
        for d in SAT_D:
            if SAT_D[d] > 0:
                rh = reference_points[d[0]]
                rh_prime = reference_points[d[1]]
                for i in range(len(rh)):
                    tmp = self.adjust_intervals(rh[i], rh_prime[i])
                    rh[i], rh_prime[i] = tmp

        # Choix des valeurs des critères dans les intervals ajustés
        for reference_point in reference_points:
            for i in range(len(reference_point)):
                criterion = random.uniform(reference_point[i][0], reference_point[i][1])
                while not criterion > reference_point[i][0]:
                    criterion = random.uniform(reference_point[i][0], rh[i][1])
                reference_point[i] = criterion

        self.RMP_model = RMP(reference_points, SAT_Y)


def generate_random_RMP_learning_set(J, N):
    result = []
    for _ in range(J):
        p = [random.random() for i in range(N)]
        n = [random.random() for i in range(N)]
        result.append((p,n))
    return result


def generate_RMP_learning_set(J, N, H):
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
    result = []
    comparison_count = 0
    while comparison_count < J:
        p = [random.random() for i in range(N)]
        n = [random.random() for i in range(N)]
        comparison = RMP_model.compare(p, n)
        if not comparison[1]:
            if comparison[0]:
                result.append((p, n))
            else:
                result.append((n, p))
            comparison_count += 1
    return result



def dominates(rh, rh_prime):
    index = 0
    while rh[index] == rh_prime[index] and index < len(rh):
        index += 1
    if rh[index] > rh_prime[index]:
        for i in range(index, len(rh)):
            if rh[i] < rh_prime[i]:
                return False
    else:
        for i in range(index, len(rh)):
            if rh[i] > rh_prime[i]:
                return False
    return True


def test_rmp(J, N, H, random_comparaisons):
    if random_comparaisons:
        comparaison_list = generate_random_RMP_learning_set(J, N)
    else:
        comparaison_list = generate_RMP_learning_set(J, N, H)
    sat_rmp = SatRmp(comparaison_list, J, H, N)
    sat_rmp.run_SAT()
    try:
        sat_rmp.create_RMP_model()
    except AssertionError:
        return False, 'UNSAT'
    except Exception:
        return False, 'RMP'
    for j in range(J):
        if not sat_rmp.RMP_model.compare(comparaison_list[j][0], comparaison_list[j][1])[0]:
            return False, 'Restitution'
    if not sat_rmp.RMP_model.domination():
        return False, 'Dominance'
    return True, sat_rmp


def test_multiple_rmp_stats(iterations, J, N, H, random_comparaisons):
    stats = {'UNSAT': 0, 'RMP': 0, 'Restitution': 0, 'Dominance': 0, 'Success': 0}
    success_models = []
    for _ in range(iterations):
        test_result = test_rmp(J, N, H, random_comparaisons)
        if test_result[0]:
            stats['Success'] += 1
            success_models.append(test_result[1])
        else:
            stats[test_result[1]] += 1
    print()
    return stats, success_models



def test_multiple_comparisons(J, N, H, iterations):
    stats = {'Indif' : 0, 'UNSAT': 0, 'RMP': 0, 'Restitution': 0, 'Dominance': 0, 'Success': 0}
    random_comparaisons = False
    test_result = test_rmp(J, N, H, random_comparaisons)
    if test_result[0]:
        print(test_result[1].RMP_model)

    sat_rmp = test_result[1]
    RMP = test_result[1].RMP_model

    comparaisons_list = sat_rmp.comparaison_list

    for i in range(iterations):

        # comparaison de deux vecteurs x et y :

        x = [random.random() for i in range(N)]
        y = [random.random() for i in range(N)]

        print(x, y)

        x_greater, indifferent = RMP.compare(x, y)
        y_greater, is_indifferent = RMP.compare(y, x)

        print(x_greater, y_greater, is_indifferent)

        # ajout de la clause dans le modèle RMP
        if not is_indifferent:
            new_comparaison_list = comparaisons_list + [(x, y) if x_greater else (y, x)]
            res, new_sat = test_rmp(J, N, H, new_comparaison_list)
            print(res, new_sat)

            if not res:
                stats[new_sat] += 1
            else:
                stats['Success'] += 1
        else:
            stats['Indif'] += 1
    print(stats)
    return None

"""J = 25
N = 4
H = 1

#test_multiple_comparisons(J, N, H, 5)

print(test_multiple_rmp_stats(10, J, N, H, False))"""


## Testing contrastive Explanation

from pysat.examples.musx import MUSX
from pysat.formula import WCNF, CNF
J = 8
N = 4
H = 2
comparaison_list = generate_RMP_learning_set(J, N, H)
sat_rmp = SatRmp(comparaison_list, J, H, N)
sat_rmp.run_SAT()
sat_rmp.create_RMP_model()
x, y = [random.random() for i in range(N)], [random.random() for i in range(N)]
comparison = sat_rmp.RMP_model.compare(x, y)
if not comparison[1]:
    if comparison[0]:
        contrastive_comparaison_list = comparaison_list + [(y, x)]
    else:
        contrastive_comparaison_list = comparaison_list + [(x, y)]
    print("Done")
else:
    print("Not done")


contrastive_sat_rmp = SatRmp(contrastive_comparaison_list, J + 1, H, N)
contrastive_sat_rmp.run_SAT()


try:
    contrastive_sat_rmp.create_RMP_model()
except AssertionError:
    print('UNSAT')
    #cnf = CNF(from_clauses=contrastive_sat_rmp.clauses)
    #wcnf = cnf.weighted()
    wcnf = WCNF()
    for i in range(len(contrastive_sat_rmp.clauses)):
        #if i < contrastive_sat_rmp.structure_clauses_index:
            #wcnf.append(contrastive_sat_rmp.clauses[i])
        #else:
        wcnf.append(contrastive_sat_rmp.clauses[i], weight=1)
    musx = MUSX(wcnf, verbosity=0)

    mus = musx.compute()
    print(mus)
else:
    mus = None
    print('SAT')



















"""
stats = test_multiple_rmp_stats(iterations, J, N, H)
print(stats[0], '\n')
for success in stats[1]:
    print(success.RMP_model)

a = {'UNSAT': 0, 'RMP': 0, 'Restitution': 0, 'Dominance': 0, 'Success': 0}
models = []
for el in log:
    models.extend(el[1])
    for key in el[0]:
        a[key] += el[0][key]

comparaison_list = generate_random_RMP_learning_set(J, N)
sat_rmp = SatRmp(comparaison_list, J, H, N)
sat_rmp.run_SAT()
sat_rmp.create_RMP_model()"""
    

