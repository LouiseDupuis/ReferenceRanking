from pysat.examples.musx import MUSX
from pysat.formula import WCNF, CNF
from SatRmp import SatRmp
from utils import *
import random

import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--J', dest='J', default=3, type = int, help='Number of comparisons in the comparison base')
    parser.add_argument('--N', dest='N', default=4, type = int, help='Number of criterions in the model')
    parser.add_argument('--H', dest='H', default=1, type = int, help='Number of reference points in the model')
    parser.add_argument('--timeout', dest='timeout', default=5, type = int, help='Timeout for the MARCO output')
    parser.add_argument('--all_mus', dest='all_mus', default=False, type = bool, help='Whether or not to output all muses including the contrastive comparison')

    args = parser.parse_args()



    # create a learning set
    J = args.J
    N = args.N
    H = args.H
    rounded = True
    comparaison_list = generate_RMP_learning_set(J, N, H, rounded)
    print("comparaison_list", comparaison_list, "\n")
    sat_rmp = SatRmp(comparaison_list, J, H, N)
    sat_rmp.run_SAT()
    sat_rmp.create_RMP_model()

    # add the contrastive comparison to the learning set and look for an unsat model
    unsat_model_found = False
    while not unsat_model_found:
        def generate_comparison(rounded):
            if rounded:
                x, y = [ round(random.random(), 2) for i in range(N)], [round(random.random(), 2) for i in range(N)]
            else:
                x, y = [ random.random() for i in range(N)], [random.random() for i in range(N)]
            return x,y
        x,y = generate_comparison(rounded)
        while test_trivial_contrastive_comparison((x,y)) or test_trivial_contrastive_comparison((y,x)):
            x,y = generate_comparison(rounded)
        comparison = sat_rmp.RMP_model.compare(x, y)
        comparison_added = False
        if not comparison[1]:
            random.shuffle(comparaison_list)
            if comparison[0]:
                contrastive_comparaison_list = comparaison_list + [(y, x)]
                contrastive_comparison = (y, x)
            else:
                contrastive_comparaison_list = comparaison_list + [(x, y)]
                contrastive_comparison = (x, y)
            comparison_added = True
        if comparison_added:
            contrastive_sat_rmp = SatRmp(contrastive_comparaison_list, J + 1, H, N)
            contrastive_sat_rmp.run_SAT()
            try:
                contrastive_sat_rmp.create_RMP_model()
            except AssertionError:
                # unsat model found 
                unsat_model_found = True
                print("Contrastive comparison : ", contrastive_comparison, "\n")
                # create a log with cnf files for the unsat model and the muses generated by marco
                marco_mus_list, iteration_number = generate_marco_mus_list(contrastive_sat_rmp, args.timeout)
                # create a mus with musx solver
                mus = generate_musx_mus(contrastive_sat_rmp, J)
                # look for mus with 2 comparisons in marco mus list
                target_muses = target_mus_lookup(contrastive_sat_rmp, marco_mus_list, J, args.all_mus)
                write_target_logs(iteration_number, target_muses, contrastive_sat_rmp)