from itertools import combinations
from bidict import bidict
import random
import pylgl
from RMP import RMP


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
        self.clauses_groups = dict( [ (i, []) for i in range(6)])
        self.clauses_names =  dict( )
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
        self.clauses_groups[1] = clause
        self.clauses_names['1'] = clause
        return clause

    def clause_2a(self):
        clause = []
        for h_prime in range(self.H):
            for h in range(h_prime + 1, self.H):
                clause.append([self.D[(h, h_prime)], self.D[(h_prime, h)]])
                self.clause_index += 1
        self.clauses_groups[2] += clause
        self.clause_names['2a'] = clause
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
        self.clauses_groups[2] += clause
        self.clause_names['2b'] = clause
        return clause

    def clause_3a(self):
        clause = []
        for partie_a, partie_b in self.Y:
            clause.append([self.Y[(partie_a, partie_b)], self.Y[(partie_b, partie_a)]])
            self.clause_index += 1
        self.clauses_groups[3] += clause
        self.clause_names['3a'] = clause
        return clause

    def clause_3b(self):
        clause = []
        for partie_a, partie_b in self.Y:
            if set(partie_b).issubset(set(partie_a)):
                clause.append([self.Y[(partie_a, partie_b)]])
                self.clause_index += 1
        self.clauses_groups[3] += clause
        self.clause_names['3b'] = clause
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
        self.clauses_groups[3] += clause
        self.clause_names['3c'] = clause
        return clause

    def clause_4a(self):
        clauses = []
        for j in range(self.J):
            clauses.append([self.S[j, h] for h in range(self.H)])
            self.comparaison_to_clause[j].append(self.clause_index)
            self.clause_index += 1
        self.clauses_groups[4] += clauses
        self.clause_names['4a'] = clauses 
        return clauses

    def clause_4b(self):
        clauses = []
        for j in range(self.J):
            for h in range(self.H):
                for h_prime in range(0, h + 1):
                    clauses.append([self.Z[j, h_prime], -self.S[j, h]])
                    self.comparaison_to_clause[j].append(self.clause_index)
                    self.clause_index += 1
        self.clauses_groups[4] += clauses
        self.clause_names['4b'] = clauses
        return clauses

    def clause_4c(self):
        clauses = []
        for j in range(self.J):
            for h_prime in range(self.H):
                for h in range(h_prime + 1, self.H):
                    clauses.append([self.Z_prime[j, h_prime], -self.S[j, h]])
                    self.comparaison_to_clause[j].append(self.clause_index)
                    self.clause_index += 1
        self.clauses_groups[4] += clauses
        self.clause_names['4c'] = clauses
        return clauses

    def clause_4d(self):
        clauses = []
        for j in range(self.J):
            for h in range(self.H):
                clauses.append([-self.Z_prime[j, h], -self.S[j, h]])
                self.comparaison_to_clause[j].append(self.clause_index)
                self.clause_index += 1
        self.clauses_groups[4] += clauses
        self.clause_names['4d'] = clauses
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
        self.clauses_groups[5] += clause
        self.clause_names['5a'] = clause
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
        self.clauses_groups[5] += clause
        self.clause_names['5b'] = clause
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
        self.clauses_groups[5] += clause
        self.clause_names['5b'] = clause
        return clause

    def initiate_clauses(self):        
        clauses =  self.clause_1() +  self.clause_2a() +  self.clause_2b() +  self.clause_3a() +  self.clause_3b() + self.clause_3c()
        self.structure_clauses_index = len(clauses)
        clauses +=  self.clause_4a() + self.clause_4b() + self.clause_4c() + self.clause_4d()
        clauses +=  self.clause_5a() + self.clause_5b() + self.clause_5c()
        self.clauses = clauses
        return clauses

    def get_clause_numbers(self, j):
        """
        Returns the index of the clauses associated with comparison j of the comparison list
        """
        return self.comparaison_to_clause[j]

    def adjust_intervals(self, interval_1, interval_2):
        if interval_1[1] < interval_2[0]:
            raise Exception("Couldn't create RMP model : interval issueS")
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
                if min_value > max_value:
                    raise Exception("Couldn't create RMP model : min_value >= max_value")
                if min_value == max_value:
                    print( 'Egalité', min_value, max_value)
                    raise Exception("Couldn't create RMP model : min_value >= max_value")
                # construction des intervals de valeurs possible pour les points de references
                reference_point_interval.append([min_value, max_value])
            reference_points.append(reference_point_interval)

        # Ajustement des intervals pour respecter la dominance entre points de references
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


    def to_gcnf_file(self, path):
        with open(path, "w") as file:
            file.write("p cnf {} {} {}\n".format(self.unique_number - 1, len(self.clauses), 5))
            for group_index, group in self.clauses_groups.items():
                for clause in group:
                    line = "{" + str(group_index) + "} "
                    for el in clause:
                        line += str(el) + ' '
                    line += "0\n"
                    file.write(line)

    def to_cnf_file(self, path):
        with open(path, "w") as file:
            file.write("p cnf {} {}\n".format(self.unique_number - 1, len(self.clauses)))
            for clause in self.clauses:
                line = ""
                for el in clause:
                    line += str(el) + ' '
                line += "0\n"
                file.write(line)