from pysat.examples.musx import MUSX
from pysat.formula import WCNF, CNF
from SatRmp import SatRmp
from utils import generate_random_RMP_learning_set, generate_RMP_learning_set, marco_mus_solver
import random

J = 3
N = 4
H = 1
rounded = False
comparaison_list = generate_RMP_learning_set(J, N, H, rounded)
print(comparaison_list)
sat_rmp = SatRmp(comparaison_list, J, H, N)


# test ecriture


sat_rmp.run_SAT()
sat_rmp.create_RMP_model()
done = False
while not done:
    if rounded:
        x, y = [ round(random.random(), 1) for i in range(N)], [round(random.random(), 1) for i in range(N)]
    else:
        x, y = [ random.random() for i in range(N)], [random.random() for i in range(N)]
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
            done = True
            print('UNSAT')
            print("Contrastive comparison : ", contrastive_comparison)
            iteration_number = 0
            with open("Logs/iteration_number.txt", "r+") as file:
                iteration_number = int(file.read()) + 1
                file.seek(0)
                file.write(str(iteration_number))
                file.truncate()
            contrastive_sat_rmp.to_cnf_file("Logs/clauses_{}.cnf".format(iteration_number))
            contrastive_sat_rmp.to_gcnf_file("Logs/clauses_{}.gcnf".format(iteration_number))
            marco_mus_solver("Logs/clauses_{}.cnf".format(iteration_number), "Logs/output_MARCO_{}.txt".format(iteration_number))

            wcnf = WCNF()
            for i in range(len(contrastive_sat_rmp.clauses)):
                if i in contrastive_sat_rmp.comparaison_to_clause[J]:
                    wcnf.append(contrastive_sat_rmp.clauses[i])
                else:
                    wcnf.append(contrastive_sat_rmp.clauses[i], weight=1)

            musx = MUSX(wcnf, verbosity=0)

            mus = musx.compute()
            
            to_print = []
            mus_comparisons = set()
            for clause in mus:
                if clause < contrastive_sat_rmp.structure_clauses_index:
                    to_print.append((clause, 'struct'))
                else:
                    for j in contrastive_sat_rmp.comparaison_to_clause:
                        if clause in contrastive_sat_rmp.comparaison_to_clause[j]:
                            to_print.append((clause, j))
                            mus_comparisons.add(j)
            print('MUS length : ', len(mus), ', comparisons included : ', mus_comparisons)
            for comp in mus_comparisons:
                print(contrastive_comparaison_list[comp])

            for comp in to_print:
                print(comp)