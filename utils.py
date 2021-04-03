from itertools import combinations
import random
from RMP import RMP
import os
from pysat.formula import WCNF, CNF
from pysat.examples.musx import MUSX




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
            p = [ round(random.random(), 2) for i in range(N)]
            n = [ round(random.random(), 2) for i in range(N)]
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


def generate_marco_mus_list(contrastive_sat_rmp, timeout = 5):
    iteration_number = 0
    with open("Logs/iteration_number.txt", "r+") as file:
        iteration_number = int(file.read()) + 1
        file.seek(0)
        file.write(str(iteration_number))
        file.truncate()
    contrastive_sat_rmp.to_cnf_file("Logs/clauses_{}.cnf".format(iteration_number))
    contrastive_sat_rmp.to_gcnf_file("Logs/clauses_{}.gcnf".format(iteration_number))
    marco_mus_solver("Logs/clauses_{}.cnf".format(iteration_number), "Logs/output_MARCO_{}.txt".format(iteration_number), timeout)
    marco_mus_list = read_marco_output("Logs/output_MARCO_{}.txt".format(iteration_number))  
    return marco_mus_list, iteration_number



def generate_musx_mus(contrastive_sat_rmp, J):
    wcnf = WCNF()
    for i in range(len(contrastive_sat_rmp.clauses)):
        if i in contrastive_sat_rmp.comparaison_to_clause[J]:
            wcnf.append(contrastive_sat_rmp.clauses[i])
        else:
            wcnf.append(contrastive_sat_rmp.clauses[i], weight=1)
    musx = MUSX(wcnf, verbosity=0)
    mus = musx.compute()
    return mus 



def read_marco_output(path):
    mus_list = []
    with open(path, "r") as file:
        for line in file:
            if line[0] == "U":
                mus_list.append(line.split()[1:])
    return mus_list


def target_mus_lookup(contrastive_sat_rmp, marco_mus_list, J, additional_mus = False):
    target_muses = []
    #contrastive_muses_stats = []
    for mus in marco_mus_list:
        mus_stats = dict()
        mus_stats['struct_number'] = 0
        mus_stats['comparison'] = []
        for name in contrastive_sat_rmp.clause_names:
            mus_stats[name] = []
        mus_comparisons = set()
        for clause in mus:
            clause_index = int(clause) -1 # MARCO outputs the index of the clause with 1-based counting

            # getting the explicit description of the clause, not just the index :
            explicit_clause = contrastive_sat_rmp.clauses[clause_index]
            if clause_index < contrastive_sat_rmp.structure_clauses_index:
                mus_stats['struct_number'] += 1
                for name, clauses in contrastive_sat_rmp.clause_names.items():
                    if explicit_clause in clauses:
                        mus_stats[name].append(get_clause_description(contrastive_sat_rmp, explicit_clause, name))
            else:
                for j, clauses in contrastive_sat_rmp.comparaison_to_clause.items():
                    if clause_index in clauses:
                        mus_comparisons.add(j)
        
        mus_stats['comparison'] = list(mus_comparisons)
        # If we find Muses with the right structure, we output them 
        if len(mus_stats['comparison']) == 2 and (J in mus_stats['comparison']): 
            explicit_comparisons = [contrastive_sat_rmp.comparaison_list[j] for j in mus_comparisons]
            target_muses.append((mus, mus_stats, explicit_comparisons))

        # adding other MUS
        if additional_mus:
            if J in mus_stats['comparison']:
                explicit_comparisons = [contrastive_sat_rmp.comparaison_list[j] for j in mus_comparisons]
                target_muses.append((mus, mus_stats, explicit_comparisons))
    
    # we also print the best muses in cases there are no Muses with the perfect structure
    # we look for Muses with the least amount of clauses and comparisons, which also contains the contrastive comparison
    #ordered_muses = sorted(contrastive_muses_stats, key = lambda mus, stats, comp : (len(stats['comparison']) + stats['struct_number']))
    #target_muses.append(ordered_muses)

    return target_muses

def test_trivial_contrastive_comparison(contrastive_comparison):
    n,p = contrastive_comparison
    for i in range(len(n)):
        if n[i] > p[i]:
            return False
    return True



def marco_mus_solver(intput_cnf, output_file, timeout = 5):
    # timeout is a number of minutes fot the timeout of the output (otherwise > 30 minutes)
    os.system("timeout " + str(timeout) + "m python3 MARCO/marco.py " + str(intput_cnf + " -v >" + str(output_file)))


def write_target_logs(iteration_number, target_muses):
    with open('logs/target_muses_' + str(iteration_number) + '.txt', 'w') as file:
                for mus, mus_stat, explicit_comparisons in target_muses:
                    file.write(str(mus) + '\n')
                    file.write(str(mus_stat) + '\n')
                    file.write(str(explicit_comparisons) + '\n')
                    file.write('\n')

def get_clause_description(rmp_model, clause, clause_name):
    if clause_name == '1':
        i, h , k_prime = rmp_model.X.inverse[clause[0]]
        i, h , k = rmp_model.X.inverse[clause[1]]
        return {'i': i, 'h': h, 'k': k, 'k_prime': k_prime}
    if clause_name == '3a':
        A, B = rmp_model.Y.inverse[clause[0]]
        return {'A': A, 'B': B}
        

