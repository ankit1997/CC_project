import math
primes = []
def prime_(x):
    if x==2:
        return 1
    if x%2==0 or x<=1:
        return 0
    p=3
    while p<=(int)(math.sqrt(x)):
        if x%p==0:
            return 0
        p+=2
    return 1

def const_primes(n):
    global primes
    if len(primes)==0:
        primes += [2]
    curr_num = primes[len(primes)-1]
    if curr_num%2==0:
        curr_num += 1
    else:
        curr_num += 2
    while len(primes)<n:
        if prime_(curr_num):
            primes += [curr_num]
        curr_num += 2
    return
        

test = (int)(input())

for t in range(test):
    n = (int)(input())
    if len(primes)<n:
        const_primes(n)
    print (primes[n-1],"\n")
