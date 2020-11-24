from math import factorial

# proof of the Gibbard-Satterthwaite theorem in the smallest non-trivial case


n = 2 # number of voters
m = 3 # number of alternative

def allVoters():
    return range(n)

def allAlternatives():
    return range(m)


# we define the list of all profiles


def allProfiles():
    return range(factorial(m) ** n)

# to model preferences, we use permutations

def nthPerm(num, mylist):
    length = len(mylist)
    if length > 1:
        pos = num // factorial(length-1)
        restnum = num - pos * factorial(length-1)
        restlist = mylist[:pos] + mylist[pos+1:]
        return [mylist[pos]] + nthPerm(restnum, restlist)
    else:
        return [mylist[0]]

# preferences (or linear orders on the set of alternatives) are modeled by number as well

def preference(i, r):
    fact = factorial(m)
    return ( r % (fact ** (i+1)) ) // (fact ** i)

def prefers(i, x, y, r):
    mylist = nthPerm(preference(i,r), list(allAlternatives()))
    return mylist.index(x) < mylist.index(y)

def top(i, x, r):
    mylist = nthPerm(preference(i,r), list(allAlternatives()))
    return mylist.index(x) == 0

def alternatives(condition):
    return [x for x in allAlternatives() if condition(x)]

def voters(condition):
    return [i for i in allVoters() if condition(i)]

def profiles(condition):
    return [r for r in allProfiles() if condition(r)]


# we define a propositionnal variable p(r,x) which means that x is one of the winning profiles for r
# they are defined as numbers as well

def posLiteral(r, x):
    return r * m + x + 1

def negLiteral(r, x):
    return (-1) * posLiteral(r, x)

def cnfAtLeastOne():
    cnf = []
    for r in allProfiles():
        cnf.append([posLiteral(r,x) for x in allAlternatives()])
    return cnf

print(cnfAtLeastOne())

def cnfResolute():
    cnf = []
    for r in allProfiles():
        for x in allAlternatives():
            for y in alternatives(lambda y : x < y):
                cnf.append([negLiteral(r,x), negLiteral(r,y)])
    return cnf

print(cnfResolute())

def cnfSurjective():
    cnf = []
    for x in allAlternatives():
        cnf.append([posLiteral(r,x) for r in allProfiles()])
    return cnf

def iVariants(i, r1, r2):
    return all(preference(j,r1) == preference(j,r2) for j in voters(lambda j : j!=i))


def cnfStrategyProof():
    cnf = []
    for i in allVoters():
        for r1 in allProfiles():
            for r2 in profiles(lambda r2 : iVariants(i,r1,r2)):
                for x in allAlternatives():
                    for y in alternatives(lambda y : prefers(i,x,y,r1)):
                        cnf.append([negLiteral(r1,y), negLiteral(r2,x)])
    return cnf

print(cnfStrategyProof())

def cnfNondictatorial():
    cnf = []
    for i in allVoters():
        clause = []
        for r in allProfiles():
            for x in alternatives(lambda x : top(i,x,r)):
                clause.append(negLiteral(r,x))
        cnf.append(clause)
    return cnf

print(cnfNondictatorial())

cnf = cnfAtLeastOne() + cnfResolute() + cnfSurjective() + cnfNondictatorial() + cnfStrategyProof()
print(cnf)

def clause_as_string(clause):
    s = ''
    for var in clause:
        s += str(var) + ' '
    s += '0'
    return s

def cnf_to_dimacs(cnf, filename):
    # transforms a clause into a dimacs file
    file = open(filename, 'w+')
    file.write("p cnf 108 1145 \n")
    for clause in cnf:
        file.write(clause_as_string(clause) + "\n")
    file.close()

cnf_to_dimacs(cnf, "full_cnf.cnf")

