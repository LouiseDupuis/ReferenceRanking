from SAT_RMP import RMP, SatRmp, generate_random_RMP_learning_set
import unittest
import sys


# unit tests and more complex tests for the functions of SAT_RMP


class TestingRMP(unittest.TestCase):
    J = 10
    H = 2
    N = 3
    SAT_solver_path = "C:\cygwin\bin\minisat.exe"

    # test de la génération de dataset aléatoire
    def test_generation(self):
        comparaison_list = generate_random_RMP_learning_set(self.J, self.N)

        self.assertEqual(len(comparaison_list), self.J)
        self.assertEqual(len(comparaison_list[0][0]), self.N)

    # test de la génération des variables
    def test_variable(self):
        comparaison_list = generate_random_RMP_learning_set(self.J, self.N)
        SAT_RMP = SatRmp(comparaison_list, self.J, self.H, self.N, self.SAT_solver_path)

        # SAT_RMP.reset() se fait a creation de l'objet SatRmp

        # verify that all variables have a unique number
        unique_numbers = list(SAT_RMP.X.values()) + list(SAT_RMP.Y.values()) + list(SAT_RMP.D.values()) + list(SAT_RMP.Z.values()) + list(SAT_RMP.Z_prime.values()) + list(SAT_RMP.S.values())
        self.assertEqual(len(unique_numbers), len(set(unique_numbers)))


    def test_clauses(self):
        # à compléter : tests sur les clauses
        self.assertEqual(True, True)

    def test_sat_solver(self):
        comparaison_list = generate_random_RMP_learning_set(self.J, self.N)
        SAT_RMP = SatRmp(comparaison_list, self.J, self.H, self.N, self.SAT_solver_path)
        # SAT_RMP.reset()

        output_file = "Test_output_3456.cnf"
        SAT_RMP.run_SAT(output_file)

        print(open(output_file, "r").read())
        self.assertIsNotNone(open(output_file, "r").readline())



if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestingRMP.J = sys.argv.pop()
        TestingRMP.H = sys.argv.pop()
        TestingRMP.N = sys.argv.pop()
    unittest.main()






