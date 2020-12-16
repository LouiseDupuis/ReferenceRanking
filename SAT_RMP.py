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

    def is_more_important_coalition(self, coalition_1, coalition_2):
        """
            fonction de comparaison de domination de deux ensembles de critères
        """
        print('coal_1', coalition_1, 'coal_2', coalition_2)
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
    
    def compare(self, object_1, object_2):
        """
            returns a tuple ( is_preferred(object_1, object_2), is_indifferent(object_1, object_2))
        """
        for reference_point in self.reference_points:
            print(reference_point)
            coalition_1 =  self.dominant_criteria_set(object_1, reference_point)
            coalition_2 =  self.dominant_criteria_set(object_2, reference_point)
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
            Xi = [self.comparaison_list[el][0][i] for el in range(self.J)] + [self.comparaison_list[el][1][i] for el in range(self.J)]
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
            Xi = [self.comparaison_list[el][0][i] for el in range(self.J)] + [self.comparaison_list[el][1][i] for el in range(self.J)]
            for h in range(self.H):
                for k in Xi:
                    for k_prime in Xi:
                        if k > k_prime:
                            clause.append([-self.X[(i, h, k_prime)], self.X[(i, h, k)]])
        return clause

    def clause_2a(self):
        clause = []
        for h_prime in range(self.H):
            for h in range(h_prime + 1, self.H):
                clause.append([self.D[(h, h_prime)], self.D[(h_prime, h)]])
        return clause

    def clause_2b(self):
        clause = []
        for i in range(self.N):
            Xi = [self.comparaison_list[el][0][i] for el in range(self.J)] + [self.comparaison_list[el][1][i] for el in range(self.J)]
            for h in range(self.H):
                for h_prime in range(self.H):
                    for k in Xi:
                        if h != h_prime:
                            clause.append([self.X[(i, h_prime, k)], -self.X[(i, h, k)], -self.D[(h, h_prime)]])
        return clause

    def clause_3a(self):
        clause = []
        for partie_a, partie_b in self.Y:
            clause.append([self.Y[(partie_a, partie_b)], self.Y[(partie_b, partie_a)]])
        return clause

    def clause_3b(self):
        clause = []
        for partie_a, partie_b in self.Y:
            if set(partie_b).issubset(set(partie_a)):
                clause.append([self.Y[(partie_a, partie_b)]])
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
                    clause.append([ -self.Y[(a, b)], -self.Y[(b, c)], self.Y[(a, c)]])
        return clause
    
    def clause_4a(self):
        clauses = []
        for j in range(self.J):
            clauses.append([ self.S[j, h] for h in range(self.H)])
        return clauses

    def clause_4b(self):
        clauses = []
        for j in range(self.J):
            for h in range(self.H):
                for h_prime in range(0, h + 1):
                    clauses.append([self.Z[j, h_prime], -self.S[j, h]])
        return clauses

    def clause_4c(self):
        clauses = []
        for j in range(self.J):
            for h_prime in range(self.H):
                for h in range(h_prime + 1, self.H):
                    clauses.append([self.Z_prime[j, h_prime], -self.S[j, h]])
        return clauses


    def clause_4d(self):
        clauses = []
        for j in range(self.J):
            for h in range(self.H):
                clauses.append([ -self.Z_prime[j, h], -self.S[j, h]])
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
                        clause_parts.append(-self.Y[(partie_a, partie_b)])
                        clause_parts.append(self.Z_prime[(j, h)])
                        clause.append(clause_parts)
        return clause
    

    def initiate_clauses(self):
        clauses =  self.clause_1() +  self.clause_2a() +  self.clause_2b() +  self.clause_3a() +  self.clause_3b()
        clauses += self.clause_3c() +  self.clause_4a() +  self.clause_4b() +  self.clause_4c() +  self.clause_5d()
        clauses += self.clause_5a() +  self.clause_5b() + self.clause_5c()
        self.clauses = clauses
        return clauses
    
    def run_SAT(self):
        self.SAT_result = pylgl.solve(self.clauses)
    
    def create_RMP_model(self):
        assert self.SAT_result != 'UNSAT', "Couldn't create RMP model"
        SAT_X, SAT_Y = dict(), dict()

        # récupérer les x et les y donnés par le solveur SAT
        for variable in self.SAT_result:
            if abs(int(variable)) in self.X.inverse:
                SAT_X[self.X.inverse[abs(int(variable))]] = int(variable)
            if abs(int(variable)) in self.Y.inverse:
                SAT_Y[self.Y.inverse[abs(int(variable))]] = int(variable)

        # contruire les profils de référence
        reference_points = []

        for h in range(self.H):
            reference_point = []
            for i in range(self.N):
                min_value, max_value = 0, 1
                Xi = [self.comparaison_list[el][0][i] for el in range(self.J)] + [self.comparaison_list[el][1][i] for el in range(self.J)]
                # on trie les K par ordre croissant :
                # Xi.sort() pas necessaire ?
                for k in Xi:
                    if SAT_X[i, h, k] > 0:
                        max_value = min(max_value, k)
                    else:
                        min_value = max(min_value, k)
                if min_value >= max_value:
                    raise Exception("Couldn't create RMP model")
                criterion = random.uniform(min_value, max_value)
                while not criterion > min_value:
                    criterion = random.uniform(min_value, max_value)
                reference_point.append(criterion)
            reference_points.append(reference_point) 
            
        self.RMP_model = RMP(reference_points, SAT_Y)
    
def generate_random_RMP_learning_set(J, N):
    result = []
    for _ in range(J):
        p = [random.random() for i in range(N)]
        n = [random.random() for i in range(N)]
        result.append((p,n))
    return result

def test_rmp(J, N, H):
    comparaison_list = generate_random_RMP_learning_set(J, N)
    sat_rmp = SatRmp(comparaison_list, J, H, N)
    sat_rmp.run_SAT()
    try:
        sat_rmp.create_RMP_model()
    except AssertionError:
        print("Problem is not solvable (UNSAT)")
        return False
    except Exception:
        print("Problem while creating RMP")
        return False
    for j in range(J):
        if not sat_rmp.RMP_model.compare(comparaison_list[j][0], comparaison_list[j][1])[0]:
            return False
    return True
    
    
if __name__ == '__main__':
    """
    J = 10
    N = 5
    H = 2
    test_rmp(J, N, H)
    """

