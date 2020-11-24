#!/usr/bin/env python
# coding: utf-8

# In[42]:


class Rmp:
    
    def __init__(self, reference_points, criteria):
        """
            reference_points : liste de dictionnaires (key : critère, valeur : evaluation du critère)
            hypothèse : les evaluations des critère sont numériques
            criteria : listes des critères
        """
        self.reference_points = reference_points
        self.criteria = criteria
        
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
            hypothèse : le critère de domination est le cardinal du groupe des critères
        """
        return len(coalition_1) >= len(coalition_2)
    
    @staticmethod
    def dominant_criteria_set(a, reference_point, criteria):
        """
            compute c(a,rh)={i∈N:ai ≥rih}
        """
        result = set()
        for criterion in criteria:
            if Rmp.is_greater_criterion(a[criterion], reference_point[criterion]):
                result.add(criterion)  
        return result
    
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


# In[ ]:




