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