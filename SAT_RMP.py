import os, sys
from itertools import combinations
from bidict import bidict
from random import randint

class RMP:
    
    def __init__(self, reference_points, coalition_importance):
        """
            reference_points : liste de dictionnaires (key : critère, valeur : evaluation du critère)
            hypothèse : les evaluations des critère sont numériques
            criteria : listes des critères
        """
        self.reference_points = reference_points
        self.criteria = list(range(len(reference_points[0])))
        self.coalition_importance = coalition_importance
        
    @staticmethod
    def is_greater_criterion(value_1, value_2):
        """
            fonction de comparaison de deux evaluations sur un point d'un meme critère
        """
        return value_1 >= value_2
    
    @staticmethod
    def is_more_important_coalition(coalition_1, coalition_2):
        """
            fonction de comparaison de domination de deux ensembles de critères
        """
        return coalition_importance[(coalition_1, coalition_2)] > 0
    
    @staticmethod
    def dominant_criteria_set(a, reference_point, criteria):
        """
            compute c(a,rh)={i∈N:ai ≥rih}
        """
        result = []
        for criterion in criteria:
            if Rmp.is_greater_criterion(a[criterion], reference_point[criterion]):
                result.append(criterion)
        return tuple(sorted(result))
    
    def compare(self, object_1, object_2):
        """
            returns a tuple ( is_preferred(object_1, object_2), is_indifferent(object_1, object_2))
        """
        for reference_point in self.reference_points:
            coalition_1 =  Rmp.dominant_criteria_set(object_1, reference_point, self.criteria)
            coalition_2 =  Rmp.dominant_criteria_set(object_2, reference_point, self.criteria)
            if not Rmp.is_more_important_coalition(coalition_2, coalition_1):
                # 1 > 2
                return True, False
            elif not Rmp.is_more_important_coalition(coalition_1, coalition_2):
                # 1 < 2
                return False, False
        return False, True



class SatRmp:
    
    unique_number = 1
    instance_id = 1
    
    def __init__(self, comparaison_list, J, H, N, SAT_solver_file, criteria_value_range):
        """
        
        """
        self.id = SatRmp.instance_id
        SatRmp.instance_id += 1
        
        self.comparaison_list = comparaison_list
        self.J = J
        self.H = H
        self.N = N
        self.SAT_solver_file = SAT_solver_file
        self.criteria_value_range = criteria_value_range
        
        self.X = None
        self.Y = None
        self.Z = None
        self.Z_prime = None
        self.D = None
        self.S = None
        self.clauses = None
        self.SAT_result = []
        self.RMP_model = None
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
        for i in range(N):
            Xi = [self.comparaison_list[el][0][i] for el in range(self.J)] + [self.comparaison_list[el][1][i] for el in range(self.J)]
            for h in range(self.H):
                for k in Xi:
                    result_dict[(i, h, k)] = SatRmp.unique_number
                    SatRmp.unique_number += 1
        return result_dict

    def initiate_y(self):
        result_dict = bidict()
        sous_parties = []
        for taille in range(self.N + 1):
            combi = list(combinations(list(range(self.N)), taille))
            sous_parties += combi
        for partie_a in sous_parties:
            for partie_b in sous_parties:
                result_dict[partie_a, partie_b] = SatRmp.unique_number
                SatRmp.unique_number += 1
        return result_dict

    def initiate_z(self):
        result_dict = bidict()
        for j in range(self.J):
            for h in range(self.H):
                result_dict[(j, h)] = SatRmp.unique_number
                SatRmp.unique_number += 1
        return result_dict

    def initiate_z_prime(self):
        result_dict = bidict()
        for j in range(self.J):
            for h in range(self.H):
                result_dict[(j, h)] = SatRmp.unique_number
                SatRmp.unique_number += 1
        return result_dict

    def initiate_d(self):
        result_dict = bidict()
        for h in range(self.H):
            for h_prime in range(self.H):
                result_dict[(h, h_prime)] = SatRmp.unique_number
                SatRmp.unique_number += 1
        return result_dict


    def initiate_s(self):
        result_dict = bidict()
        for j in range(self.J):
            for h in range(self.H):
                result_dict[(j, h)] = SatRmp.unique_number
                SatRmp.unique_number += 1
        return result_dict

    def clause_1():
        clause = []
        for i in range(self.N):
            Xi = [self.comparaison_list[el][0][i] for el in range(self.J)] + [self.comparaison_list[el][1][i] for el in range(self.J)]
            for h in range(self.H):
                for k in Xi:
                    for k_prime in Xi:
                        if k > k_prime:
                            clause.append([-self.X[(i, h, k_prime)], self.X[(i, h, k)]])
        return clause

    def clause_2a():
        clause = []
        for h in range(self.H):
            for h_prime in range(h + 1, self.H):
                clause.append([self.D[(h, h_prime)], self.D[(h_prime, h)]])
        return clause

    def clause_2b():
        clause = []
        for i in range(self.N):
            Xi = [self.comparaison_list[el][0][i] for el in range(self.J)] + [self.comparaison_list[el][1][i] for el in range(self.J)]
            for k in Xi:
                for h in range(self.H):
                    for h_prime in range(h_prime):
                        if h != h_prime:
                            clause.append([self.X[(i, h_prime, k)], -self.X[(i, h, k)], -self.D[(h, h_prime)]])
        return clause

    def clause_3a():
        clause = []
        for partie_a, partie_b in self.Y:
            clause.append([self.Y[(partie_a, partie_b)], self.Y[(partie_b, partie_a)]])
        return clause

    def clause_3b():
        clause = []
        for partie_a, partie_b in self.Y:
            if set(partie_a).issubset(set(partie_b)):
                clause.append([self.Y[(partie_b, partie_a)]])
        return clause

    def clause_3c():
        clause = []
        sous_parties = []
        for taille in range(self.N + 1):
            combi = list(combinations(list(range(self.N)), taille))
            sous_parties += combi

        for a in sous_parties:
            for b in sous_parties:
                for c in sous_parties:
                    clause.append([ -self.Y[(a, b)], -self.Y[(b, c)], self.Y[(a, c)]])
        return clause

    def clause_4a():
        clause = []
        for partie_a, partie_b in self.Y:
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
        return clause

    def clause_4b():
        clause = []
        for partie_a, partie_b in self.Y:
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
        return clause

    def clause_4c():
        clause = []
        for partie_a, partie_b in self.Y:
            for j in range(self.J):
                for h in range(self.H):
                    clause_parts = []
                    for i in range(self.N):
                        if i in partie_a:
                            clause_parts.append(-self.X[(i, h, self.comparaison_list[j][0][i])])
                        else:
                            clause_parts.append(self.X[(i, h, self.comparaison_list[j][0][i])])
                        if i in partie_b:
                            clause_parts.append(-self.X[(i, h, self.comparaison_list[j][1][i])])
                        else:
                            clause_parts.append(self.X[(i, h, self.comparaison_list[j][0][i])])
                    clause_parts.append(-self.Y[(partie_b, partie_a)])
                    clause_parts.append(self.Z_prime[(j, h)])
                    clause.append(clause_parts)
        return clause

    def clause_5a():
        clauses = []
        for j in range(self.J):
            for h in range(self.H):
                for h_prime in range(h + 1, self.H):
                    clauses.append([self.Z[j, h], -self.S[j, h_prime]])
        return clauses

    def clause_5b():
        clauses = []
        for j in range(self.J):
            for h in range(self.H):
                for h_prime in range(h + 1, self.H):
                    clauses.append([self.Z_prime[j, h], -self.S[j, h_prime]])
        return clauses


    def clause_5c():
        clauses = []
        for j in range(self.J):
            for h in range(self.H):
                clauses.append([ -self.Z_prime[j, h], -self.S[j, h]])
        return clauses

    def clause_6():
        clauses = []
        for j in range(self.J):
            clauses.append([self.S[j, h] for h in range(self.H)])
        return clauses

    def initiate_clauses(self):
        clauses =  self.clause_1 +  self.clause_2a +  self.clause_2b +  self.clause_3a +  self.clause_3b
        clauses += self.clause_3c +  self.clause_4a +  self.clause_4b +  self.clause_4c +  self.clause_5a
        clauses += self.clause_5b +  self.clause_5c +  self.clause_6
        return clauses
    
    def run_SAT(self, result_file_path):
        clauses_file_path = 'SAT_RMP_clauses_{}.cnf'.format(self.id)
        # Creating clause file
        clauses_file = open(clauses_file_path, 'w+')
        file.write("p cnf 108 1145 \n")
        
        for clause in self.clauses:
            line = ''
            for variable in clause:
                line += str(variable) + ' '
            line += '0'
            clauses_file.write(line + "\n")
            
        clauses_file.close()
        
        # Running SAT solver
        os.system('python3 {} {} {}'.format(self.SAT_file, clauses_file_path, result_file_path))
        
    def read_SAT_result_from_file(self, result_file_path):
        result_file = open(result_file_path, 'r')
        for index, line in enumerate(result_file):
            if line.strip() == 'UNSAT':
                self.SAT_result += 'UNSAT'
                break
            elif index > 0:
                self.SAT_result += line.strip().split()[:-1]
    
    def create_RMP_model(self):
        assert len(self.SAT_result) == 0 or self.SAT_result[0] != 'UNSAT' , "Couldn't create RMP model"
        SAT_X, SAT_Y = dict(), dict()
        for variable in self.SAT_result:
            if abs(int(variable)) in self.X.inverse:
                SAT_X[self.X.inverse[int(variable)]] = int(variable)
            if abs(int(variable)) in self.Y.inverse:
                SAT_Y[self.Y.inverse[int(variable)]] = int(variable)
        reference_points = []
        for _ in range(self.H):
            reference_point = []
            for i in range(self.N):
                min_value, max_value = self.criteria_value_range[0], self.criteria_value_range[1]
                Xi = [self.comparaison_list[el][0][i] for el in range(self.J)] + [self.comparaison_list[el][1][i] for el in range(self.J)]
                for h in range(self.H):
                    for k in Xi:
                        if SAT_X[i, h, k] > 0:
                            max_value = min(max_value, k)
                        else:
                            min_value = max(min_value, k)
                if min_value + 1 > max_value:
                    raise Exception("Couldn't create RMP model")
                reference_point.append(randint(min_value + 1, max_value))
            reference_points.append(reference_point)
        self.RMP_model = RMP(reference_points, SAT_Y)


def gerenate_random_RMP_learning_set(J, N, criteria_value_range):
    result = []
    for _ in range(J):
        p = [randint(criteria_value_range[0], criteria_value_range[1]) for i in range(N)]
        n = [randint(criteria_value_range[0], criteria_value_range[1]) for i in range(N)]
        result.append((p,n))
    return result
    
    
if __name__ == __main__:
    '''
    J = 10
    N = 5
    H = 2
    SAT_solver_file = ''
    criteria_value_range = (1,100)
    result_file_path = 'SAT_output.cnf'
    comparaison_list = gerenate_random_RMP_learning_set(J, N, criteria_value_range)
    sat_rmp = SatRmp(comparaison_list, J, H, N, SAT_solver_file, criteria_value_range)
    sat_rmp.run_SAT(result_file_path)
    sat_rmp.read_SAT_result_from_file(result_file_path)
    try:
        sat_rmp.create_RMP_model()
    except AssertionError:
        print("Problem is not solvable (UNSAT)")
    except Exception:
        print("Problem while creating RMP")
    '''
