import argparse


class LipschitzConstantEstimator:
    def __init__(self):
        pass


class APrioriGivenEstimate(LipschitzConstantEstimator):
    def __init__(self, L):
        self.L = L
    
    def get(self, x, z):
        l = [self.L] * len(x)
        return l


def find_local_tuning_info(r, x, z):
    H = [0] * len(x)
    H_k = 0
    for i in range(1, len(x)):
        H[i] = abs(z[i] - z[i-1]) / max(x[i] - x[i-1], 1e-8)
        H_k = max(H_k, H[i])
    lamb = [0] * len(x)
    for i in range(1, len(x)):
        lamb[i] = max(H[i-1], H[i])
        if i + 1 < len(x):
            lamb[i] = max(lamb[i], H[i+1])
    X_max = 0
    for i in range(1, len(x)):
        X_max = max(X_max, x[i] - x[i-1])
    gamma = [0] * len(x)
    for i in range(1, len(x)):
        gamma[i] = H_k * (x[i] - x[i-1]) / X_max
    return H_k, H, lamb, gamma


class GlobalEstimate(LipschitzConstantEstimator):
    def __init__(self, r=2, xi=1e-8):
        self.r = r
        self.xi = xi

    def get(self, x, z):
        H_k, _, _, _ = find_local_tuning_info(self.r, x, z)
        l = [self.r * max(H_k, self.xi)] * len(x)
        return l


class MaximumLocalTuning(LipschitzConstantEstimator):
    def __init__(self, r=2, xi=1e-8):
        self.r = r
        self.xi = xi

    def get(self, x, z):
        _, _, lamb, gamma = find_local_tuning_info(self.r, x, z)
        l = [0] * len(x)
        for i in range(1, len(x)):
            l[i] = self.r * max(lamb[i], gamma[i], self.xi)
        return l
    

class AdditiveLocalTuning(LipschitzConstantEstimator):
    def __init__(self, r=2, xi=1e-8):
        self.r = r
        self.xi = xi

    def get(self, x, z):
        _, _, lamb, gamma = find_local_tuning_info(self.r, x, z)
        l = [0] * len(x)
        for i in range(1, len(x)):
            l[i] = self.r * max((lamb[i] + gamma[i]) / 2, self.xi)
        return l


class MaximumAdditiveLocalTuning(LipschitzConstantEstimator):
    def __init__(self, r=2, xi=1e-8):
        self.r = r
        self.xi = xi

    def get(self, x, z):
        _, H, lamb, gamma = find_local_tuning_info(self.r, x, z)
        l = [0] * len(x)
        for i in range(1, len(x)):
            l[i] = self.r * max(H[i], (lamb[i] + gamma[i]) / 2, self.xi)
        return l


class CharacteristicCalculator:
    def __init__(self):
        pass


class GeometricMethod(CharacteristicCalculator):
    def get(self, x, z, l):
        R = [0] * len(x)
        for i in range(1, len(x)):
            R[i] = (z[i] + z[i-1]) / 2 - l[i] * (x[i] - x[i-1]) / 2
        return R


class InformationMethod(CharacteristicCalculator):
    def get(self, x, z, l):
        R = [0] * len(x)
        for i in range(1, len(x)):
            R[i] = 2 * (z[i] + z[i-1]) - l[i] * (x[i] - x[i-1]) 
            R[i] -= (z[i] - z[i-1])**2 / (l[i] * max(x[i] - x[i-1], 1e-8))
        return R


class SubintervalSelector:
    def __init__(self):
        pass


def select_global(R):
    t = 1
    for i in range(1, len(R)):
        if R[i] < R[t]:
            t = i
    return t


class GlobalPhase(SubintervalSelector):
    def get(self, global_phase, x, z, R, i_min, last_pick_was_optimal):
        return select_global(R)


def select_local(R, i_min, last_pick_was_optimal, choose_right):
    if last_pick_was_optimal:
        t = i_min
        if i_min + 1 < len(R) and R[i_min + 1] < R[i_min]:
            t = i_min + 1
        return t, False
    if i_min + 1 == len(R):
        return i_min, False
    if choose_right:
        return i_min + 1, True
    else:
        return i_min, True


class PessimisticLocalImprovement(SubintervalSelector):
    def __init__(self, delta):
        self.delta = delta
        self.choose_right = True
        
    def get(self, global_phase, x, z, R, i_min, last_pick_was_optimal):
        if global_phase:
            return select_global(R)
        t, change = select_local(R, i_min, last_pick_was_optimal, self.choose_right)
        if change:
            self.choose_right ^= True
        if x[t] - x[t-1] <= self.delta:
            return select_global(R)
        return t


class OptimisticLocalImprovement(SubintervalSelector):
    def __init__(self):
        self.choose_right = True

    def get(self, global_phase, x, z, R, i_min, last_pick_was_optimal):
        if global_phase:
            return select_global(R)
        t, change = select_local(R, i_min, last_pick_was_optimal, self.choose_right)
        if change:
            self.choose_right ^= True
        return t


class Algorithm:
    def __init__(self, 
            lipschitz_constant_estimator,
            characteristic_calculator,
            subinterval_selector):
        self.estimator = lipschitz_constant_estimator
        self.calculator = characteristic_calculator
        self.selector = subinterval_selector
        

def find_min(f, a, b, eps, algo):
    x = [a, b]
    z = [f(a), f(b)]
    global_phase = True
    last_pick_was_optimal = False
    while True:
        x, z = zip(*sorted(zip(x, z)))
        x = list(x)
        z = list(z)
        i_min = 0
        for i in range(len(z)):
            if z[i] < z[i_min]:
                i_min = i
        l = algo.estimator.get(x, z)
        R = algo.calculator.get(x, z, l)
        t = algo.selector.get(global_phase, x, z, R, i_min, last_pick_was_optimal)
        global_phase ^= True
        if x[t] - x[t-1] <= eps:
            break
        new_x = (x[t] + x[t-1]) / 2 - (z[t] - z[t-1]) / (2 * l[t])
        if new_x < a:
            new_x = a + eps
        if new_x > b:
            new_x = b - eps
        x.append(new_x)
        z.append(f(new_x))
        if not z[-1]:
            break
        if z[-1] <= z[i_min]:
            last_pick_was_optimal = True
        else:
            last_pick_was_optimal = False
    return x[i_min], z[i_min]


def eval_at(x):
    eval_at.queries += 1
    if eval_at.queries >= 1000:
        return None

    # problem 0
    #return -1/(3.9780059916004804 * (10. * x - 1.6649929909253236)**2 + 0.1828660559365029) + -1/(5.411447363092992 * (10. * x - 2.285771292848484)**2 + 0.19045310811228205) + -1/(1.5509459490118427 * (10. * x - 4.351900476783807)**2 + 0.2133907015534809) + -1/(6.837307598441257 * (10. * x - 1.3211760765629055)**2 + 0.15969534790691786) + -1/(8.09488104211493 * (10. * x - 0.14614859392490298)**2 + 0.15598192319264903) + -1/(1.720616784301353 * (10. * x - 6.845816224995192)**2 + 0.28814985449898023) + -1/(2.0666392669257765 * (10. * x - 8.40964462436705)**2 + 0.22578064439908463) + -1/(1.021664022653415 * (10. * x - 0.5568973164655067)**2 + 0.12329325847923694) + -1/(2.4895318572292244 * (10. * x - 6.822806782090089)**2 + 0.20157771231795837) + -1/(7.888471758225953 * (10. * x - 5.864422048183654)**2 + 0.10677826382200935)

    # problem 10
    #return 1./(2.2956524158282527 * (10. * x - 2.5300315045845445)**2 + 0.17254428083919665) + 1./(3.477868734710947 * (10. * x - 8.695815637869055)**2 + 0.26671506054289584) + 1./(2.112608744084211 * (10. * x - 0.12439904596048157)**2 + 0.26521075798289256) + 1./(1.0392399872676419 * (10. * x - 7.100102175995801)**2 + 0.18169944771552657) + 1./(1.1804165239446527 * (10. * x - 1.6267308890404397)**2 + 0.26604930606824645) + 1./(8.511095079397414 * (10. * x - 8.908965289190727)**2 + 0.26224413435699534) + 1./(4.8724207824842445 * (10. * x - 1.6001932498184024)**2 + 0.24932232379628563) + 1./(4.714909387073538 * (10. * x - 4.162389956816165)**2 + 0.1635221039339777) + 1./(3.1220637491214847 * (10. * x - 8.902428046265955)**2 + 0.14255119556734894) + 1./(8.14718352927964 * (10. * x - 3.9415799386587667)**2 + 0.2931701869766348)

    print("%.10f" % x, flush=True)
    return float(input())
eval_at.queries = 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read algorithm parameters')
    parser.add_argument('--area-begin', type=float, required=True)
    parser.add_argument('--area-end', type=float, required=True)
    parser.add_argument('--precision', type=float, required=True)
    parser.add_argument('--max-slope', type=float, required=True)
    parser.add_argument('--algorithm', type=str, required=False)
    args = parser.parse_args()

    name = args.algorithm
    if not name:
        name = 'Inf-LTMA'

    if name == 'Geom-AL':
        algo = Algorithm(APrioriGivenEstimate(args.max_slope), GeometricMethod(),
        GlobalPhase())
    elif name == 'Geom-GL':
        algo = Algorithm(GlobalEstimate(), GeometricMethod(), GlobalPhase())
    elif name == 'Geom-LTM':
        algo = Algorithm(MaximumLocalTuning(), GeometricMethod(), GlobalPhase())
    elif name == 'Geom-LTA':
        algo = Algorithm(AdditiveLocalTuning(), GeometricMethod(), GlobalPhase())
    elif name == 'Geom-LTMA':
        algo = Algorithm(MaximumAdditiveLocalTuning(), GeometricMethod(), 
        GlobalPhase())
    elif name == 'Geom-LTIMP':
        algo = Algorithm(MaximumLocalTuning(), GeometricMethod(),
        PessimisticLocalImprovement(args.precision))
    elif name == 'Geom-LTIAP':
        algo = Algorithm(AdditiveLocalTuning(), GeometricMethod(),
        PessimisticLocalImprovement(args.precision))
    elif name == 'Geom-LTIMAP':
        algo = Algorithm(MaximumAdditiveLocalTuning(), GeometricMethod(),
        PessimisticLocalImprovement(args.precision))
    elif name == 'Geom-LTIMO':
        algo = Algorithm(MaximumLocalTuning(), GeometricMethod(),
        OptimisticLocalImprovement())
    elif name == 'Geom-LTIAO':
        algo = Algorithm(AdditiveLocalTuning(), GeometricMethod(),
        OptimisticLocalImprovement())
    elif name == 'Geom-LTIMAO':
        algo = Algorithm(MaximumAdditiveLocalTuning(), GeometricMethod(),
        OptimisticLocalImprovement())
    elif name == 'Inf-AL':
        algo = Algorithm(APrioriGivenEstimate(args.max_slope), InformationMethod(),
        GlobalPhase())
    elif name == 'Inf-GL':
        algo = Algorithm(GlobalEstimate(), InformationMethod(), GlobalPhase())
    elif name == 'Inf-LTM':
        algo = Algorithm(MaximumLocalTuning(), InformationMethod(), GlobalPhase())
    elif name == 'Inf-LTA': 
        algo = Algorithm(AdditiveLocalTuning(), InformationMethod(), GlobalPhase())
    elif name == 'Inf-LTMA':
        algo = Algorithm(MaximumAdditiveLocalTuning(), InformationMethod(), 
        GlobalPhase())
    elif name == 'Inf-LTIMP':
        algo = Algorithm(MaximumLocalTuning(), InformationMethod(),
        PessimisticLocalImprovement(args.precision))
    elif name == 'Inf-LTIAP':
        algo = Algorithm(AdditiveLocalTuning(), InformationMethod(),
        PessimisticLocalImprovement(args.precision))
    elif name == 'Inf-LTIMAP':
        algo = Algorithm(MaximumAdditiveLocalTuning(), InformationMethod(),
        PessimisticLocalImprovement(args.precision))
    elif name == 'Inf-LTIMO':
        algo = Algorithm(MaximumLocalTuning(), InformationMethod(),
        OptimisticLocalImprovement())
    elif name == 'Inf-LTIAO':
        algo = Algorithm(AdditiveLocalTuning(), InformationMethod(),
        OptimisticLocalImprovement())
    elif name == 'Inf-LTIMAO':
        algo = Algorithm(MaximumAdditiveLocalTuning(), InformationMethod(),
        OptimisticLocalImprovement())
    else:
        raise ValueError('Incorrect algorithm name')

    arg, val = find_min(eval_at, args.area_begin, args.area_end, args.precision, algo)
    print('STOP\n', "%.10f\n" % arg, "%.10f" % val, sep='', flush=True)
    print('Queries:', eval_at.queries)

