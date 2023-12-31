
'''
USAGE:
test = ExpRandom()
test.next()
'''

class Rand48(object):
    def __init__(self, seed=0):
        self.n = seed
    def seed(self, seed):
        self.n = seed
    def srand(self, seed):
        self.n = (seed << 16) + 0x330e
    def next(self):
        self.n = (25214903917 * self.n + 11) & (2**48 - 1)
        return self.n
    def drand(self):
        return self.next() / 2**48
    def lrand(self):
        return self.next() >> 17
    def mrand(self):
        n = self.next() >> 16
        if n & (1 << 31):
            n -= 1 << 32
        return n

if __name__ == "__main__":
    test = Rand48()
    test.srand(2)
    for i in range(10):
        print(test.drand())