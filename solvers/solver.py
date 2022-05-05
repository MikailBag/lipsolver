import argparse
import math


class LipschitzConstantEstimator:
    def __init__(self):
        pass


class APrioriGivenEstimate(LipschitzConstantEstimator):
    def __init__(self, l_global):
        self.l_global = l_global
    
    def get(self, x, z):
        l = [0]
        l.extend([self.l_global] * (len(x) - 1))
        return l


class CharacteristicCalculator:
    def __init__(self):
        pass


class GeometricMethod(CharacteristicCalculator):
    def get(self, x, z, l):
        r = [0]
        r.extend([(z[i] + z[i-1]) / 2 - l[i] * (x[i] - x[i-1]) / 2 for i in range(1, len(x))])
        return r


class SubintervalSelector:
    def __init__(self):
        pass


class OptimisticLocalImprovement(SubintervalSelector):
    def get(self, global_phase, x, r, t):
        return t


class Algorithm:
    def __init__(self, 
            lipschitz_constant_estimator,
            characteristics_calculator,
            subinterval_selector):
        self.estimator = lipschitz_constant_estimator
        self.calculator = characteristics_calculator
        self.selector = subinterval_selector
        

def find_min(f, a, b, eps, algo):
    x = [a, b]
    z = [f(a), f(b)]
    k = 2
    global_phase = True
    i_min = 0
    while True:
        x, z = zip(*sorted(zip(x, z)))
        x = list(x)
        z = list(z)
        i_min = 0
        for i in range(len(z)):
            if z[i] < z[i_min]:
                i_min = i

        l = algo.estimator.get(x, z)
        r = algo.calculator.get(x, z, l)
        t = 1
        if global_phase:
            for i in range(1, len(r)):
                if r[i] < r[t]:
                    t = i
        else:
            # not exactly as in the paper
            if i_min == 0:
                t = 1
            else:
                t = i_min
        t = algo.selector.get(global_phase, x, r, t)
        global_phase = not global_phase
        if x[t] - x[t-1] <= eps:
            break
        new_x = (x[t] + x[t-1]) / 2 - (z[t] - z[t-1]) / (2 * l[t])
        x.append(new_x)
        z.append(f(new_x))
        k += 1
    return z[i_min]


def eval_at(x):
    print("%.10f" % x, flush=True)
    return float(input())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read algorithm parameters')
    parser.add_argument('--area_begin', type=float, required=True)
    parser.add_argument('--area_end', type=float, required=True)
    parser.add_argument('--precision', type=float, required=True)
    args = parser.parse_args()
      
    algo = Algorithm(APrioriGivenEstimate(10), GeometricMethod(), OptimisticLocalImprovement())

    result = find_min(eval_at, args.area_begin, args.area_end, args.precision, algo)
    print('STOP\n', "%.10f" % result, sep='', flush=True)

