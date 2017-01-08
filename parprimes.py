from epypes.patterns.wpool import ProcessWorkersPoolNode
from epypes.pipeline import Node

if __name__ == '__main__':

    PRIMES = [
    112272535095293,
    112582705942171,
    112272535095293,
    115280095190773,
    115797848077099,
    1099726899285419]

    def is_prime(n):
        import math
        if n % 2 == 0:
            return False

        sqrt_n = int(math.floor(math.sqrt(n)))
        for i in range(3, sqrt_n + 1, 2):
            if n % i == 0:
                return False
        return True

    def series(primes):
        res = {}
        for p in primes:
            pred = is_prime(p)
            res[p] = pred
        return res

    pnode = ProcessWorkersPoolNode('IsPrime', is_prime)
    snode = Node('IsPrimeSerial', series)

    res1 = pnode.run(PRIMES)
    res2 = snode.run(PRIMES)

    print(pnode, pnode.time)
    print(snode, snode.time)
